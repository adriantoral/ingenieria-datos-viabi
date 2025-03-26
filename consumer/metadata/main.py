import json
import os
import sys
from datetime import datetime, timezone

from influxdb_client import InfluxDBClient, Point
from pika import BlockingConnection, ConnectionParameters, PlainCredentials

CONFIG_INFLUX = {
	'url'   : os.getenv( 'CONFIG_INFLUX_URL' ),
	'token' : os.getenv( 'CONFIG_INFLUX_TOKEN' ),
	'org'   : os.getenv( 'CONFIG_INFLUX_ORG' ),
	'bucket': os.getenv( 'CONFIG_INFLUX_BUCKET' )
}

CONFIG_RABBITMQ_META = {
	'url'     : os.getenv( 'CONFIG_RABBITMQ_URL' ),
	'username': os.getenv( 'CONFIG_RABBITMQ_USERNAME' ),
	'password': os.getenv( 'CONFIG_RABBITMQ_PASSWORD' ),
	'queue'   : os.getenv( 'CONFIG_RABBITMQ_QUEUE_META' )
}


def upload_metadata_to_influx ( influx, metadata ):
	point = (
		Point( "intrusion_event" )
		.tag( "image_name", metadata['image_name'] )
		.field( "probability", metadata['probability'] )
		.field( "image_url", metadata['image_url'] )
		.time( datetime.now( timezone.utc ).isoformat( ) )
	)
	write_api = influx.write_api( )
	write_api.write( bucket=CONFIG_INFLUX['bucket'], record=point )
	write_api.close( )


def callback ( influx, ch, method, properties, body ):
	try:
		data = json.loads( body.decode( ) )
		upload_metadata_to_influx( influx, data )
		ch.basic_ack( delivery_tag=method.delivery_tag )
	except Exception as e:
		print( f"Error en callback metadatos: {e}" )
		ch.basic_nack( delivery_tag=method.delivery_tag, requeue=False )


def main ( ):
	influx_client = InfluxDBClient(
		url=CONFIG_INFLUX['url'],
		token=CONFIG_INFLUX['token'],
		org=CONFIG_INFLUX['org']
	)

	rabbit_client = BlockingConnection(
		ConnectionParameters(
			host=CONFIG_RABBITMQ_META['url'].split( ':' )[0],
			port=int( CONFIG_RABBITMQ_META['url'].split( ':' )[1] ),
			credentials=PlainCredentials( CONFIG_RABBITMQ_META['username'], CONFIG_RABBITMQ_META['password'] )
		)
	)

	channel = rabbit_client.channel( )
	channel.queue_declare( queue=CONFIG_RABBITMQ_META['queue'], durable=True )
	channel.basic_consume(
		queue=CONFIG_RABBITMQ_META['queue'], auto_ack=False,
		on_message_callback=lambda ch, method, props, body: callback( influx_client, ch, method, props, body )
	)
	print( "Consumer de metadatos iniciado" )

	try: channel.start_consuming( )
	except KeyboardInterrupt:
		influx_client.close( )
		rabbit_client.close( )
		sys.exit( 0 )


if __name__ == '__main__':
	main( )
