import os
import random
import signal
import sys
from datetime import datetime, timezone
from io import BytesIO

from influxdb_client import InfluxDBClient, Point
from minio import Minio
from pika import BlockingConnection, ConnectionParameters, PlainCredentials

CONFIG_MINIO = {
	'url'       : os.getenv( 'CONFIG_MINIO_URL' ),
	'access_key': os.getenv( 'CONFIG_MINIO_ACCESS_KEY' ),
	'secret_key': os.getenv( 'CONFIG_MINIO_SECRET_KEY' ),
	'bucket'    : os.getenv( 'CONFIG_MINIO_BUCKET' )
}

CONFIG_INFLUX = {
	'url'   : os.getenv( 'CONFIG_INFLUX_URL' ),
	'token' : os.getenv( 'CONFIG_INFLUX_TOKEN' ),
	'org'   : os.getenv( 'CONFIG_INFLUX_ORG' ),
	'bucket': os.getenv( 'CONFIG_INFLUX_BUCKET' )
}

CONFIG_RABBITMQ = {
	'url'     : os.getenv( 'CONFIG_RABBITMQ_URL' ),
	'username': os.getenv( 'CONFIG_RABBITMQ_USERNAME' ),
	'password': os.getenv( 'CONFIG_RABBITMQ_PASSWORD' ),
	'queue'   : os.getenv( 'CONFIG_RABBITMQ_QUEUE' )
}


def try_catch_decorator ( func ):
	def wrapper ( *args, **kwargs ):
		try:
			return func( *args, **kwargs )
		except Exception as e:
			print( f"Error: {e}" )
			return None

	return wrapper


def create_instances ( ):
	_minio_client = Minio(
		CONFIG_MINIO['url'],
		access_key=CONFIG_MINIO['access_key'],
		secret_key=CONFIG_MINIO['secret_key'],
		secure=False
	)

	_influx_client = InfluxDBClient(
		url=CONFIG_INFLUX['url'],
		token=CONFIG_INFLUX['token'],
		org=CONFIG_INFLUX['org']
	)

	_rabbitmq_client = BlockingConnection(
		ConnectionParameters(
			host=CONFIG_RABBITMQ['url'].split( ':' )[0],
			port=int( CONFIG_RABBITMQ['url'].split( ':' )[1] ),
			credentials=PlainCredentials( CONFIG_RABBITMQ['username'], CONFIG_RABBITMQ['password'] )
		)
	)

	return _minio_client, _influx_client, _rabbitmq_client


@try_catch_decorator
def upload_image_to_minio ( minio, image_bytes ):
	image_name = f"intrusion_{datetime.now( timezone.utc ).strftime( '%Y%m%d%H%M%S%f' )}.jpg"

	minio.put_object(
		CONFIG_MINIO['bucket'],
		image_name,
		BytesIO( image_bytes ),
		len( image_bytes )
	)

	return image_name, minio.presigned_get_object(
		CONFIG_MINIO['bucket'],
		image_name,
		response_headers={
			"Content-Type"       : "image/jpeg",
			"Content-Disposition": "inline"
		}
	)


@try_catch_decorator
def upload_image_to_influx ( influx, image_name, image_url ):
	point = (
		Point( "intrusion_event" )
		.tag( "image_name", image_name )
		.field( "probability", random.randint( 0, 100 ) / 100 )
		.field( "image_url", image_url )
		.time( datetime.now( timezone.utc ).isoformat( ) )
	)

	write_api = influx.write_api( )
	write_api.write( bucket=CONFIG_INFLUX['bucket'], record=point )
	write_api.close( )


@try_catch_decorator
def callback ( minio, influx, ch, method, properties, body ):
	print( 'OK: ', body[:10], '...' )

	image_name, image_url = upload_image_to_minio( minio, body )
	if image_url: upload_image_to_influx( influx, image_name, image_url )

	ch.basic_ack( delivery_tag=method.delivery_tag )


@try_catch_decorator
def signal_handler ( influx, rabbit, sig, frame ):
	if influx: influx.close( )
	if rabbit: rabbit.close( )
	sys.exit( 0 )


if __name__ == '__main__':
	minio_client, influx_client, rabbitmq_client = create_instances( )

	# Capturar señales para cerrar correctamente
	signal.signal( signal.SIGINT, lambda sig, frame: signal_handler( influx_client, rabbitmq_client, sig, frame ) )
	signal.signal( signal.SIGTSTP, lambda sig, frame: signal_handler( influx_client, rabbitmq_client, sig, frame ) )
	signal.signal( signal.SIGTERM, lambda sig, frame: signal_handler( influx_client, rabbitmq_client, sig, frame ) )

	channel = rabbitmq_client.channel( )
	channel.queue_declare( queue=CONFIG_RABBITMQ['queue'] )
	channel.basic_consume(
		queue=CONFIG_RABBITMQ['queue'],
		auto_ack=True,
		on_message_callback=lambda ch, method, properties, body: callback(
			minio_client,
			influx_client,
			ch,
			method,
			properties,
			body
		)
	)

	try:
		channel.start_consuming( )
	except KeyboardInterrupt:
		signal_handler( influx_client, rabbitmq_client, None, None )
