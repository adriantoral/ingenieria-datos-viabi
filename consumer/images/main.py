import os
import sys
from datetime import datetime, timezone
from io import BytesIO

from minio import Minio
from pika import BlockingConnection, ConnectionParameters, PlainCredentials

CONFIG_MINIO = {
	'url'       : os.getenv( 'CONFIG_MINIO_URL' ),
	'access_key': os.getenv( 'CONFIG_MINIO_ACCESS_KEY' ),
	'secret_key': os.getenv( 'CONFIG_MINIO_SECRET_KEY' ),
	'bucket'    : os.getenv( 'CONFIG_MINIO_BUCKET' )
}

CONFIG_RABBITMQ_IMG = {
	'url'     : os.getenv( 'CONFIG_RABBITMQ_URL' ),
	'username': os.getenv( 'CONFIG_RABBITMQ_USERNAME' ),
	'password': os.getenv( 'CONFIG_RABBITMQ_PASSWORD' ),
	'queue'   : os.getenv( 'CONFIG_RABBITMQ_QUEUE_IMG' )
}


def upload_image_to_minio ( minio, image_bytes ):
	image_name = f"intrusion_{datetime.now( timezone.utc ).strftime( '%Y%m%d%H%M%S%f' )}.jpg"
	minio.put_object(
		CONFIG_MINIO['bucket'],
		image_name,
		BytesIO( image_bytes ),
		len( image_bytes )
	)
	print( f"Imagen subida a MinIO: {image_name}" )


def callback ( minio, ch, method, properties, body ):
	try:
		upload_image_to_minio( minio, body )
		ch.basic_ack( delivery_tag=method.delivery_tag )
	except Exception as e:
		print( f"Error en callback imagen: {e}" )
		ch.basic_nack( delivery_tag=method.delivery_tag, requeue=False )


def main ( ):
	minio_client = Minio(
		CONFIG_MINIO['url'],
		access_key=CONFIG_MINIO['access_key'],
		secret_key=CONFIG_MINIO['secret_key'],
		secure=False
	)

	rabbit_client = BlockingConnection(
		ConnectionParameters(
			host=CONFIG_RABBITMQ_IMG['url'].split( ':' )[0],
			port=int( CONFIG_RABBITMQ_IMG['url'].split( ':' )[1] ),
			credentials=PlainCredentials( CONFIG_RABBITMQ_IMG['username'], CONFIG_RABBITMQ_IMG['password'] )
		)
	)

	channel = rabbit_client.channel( )
	channel.queue_declare( queue=CONFIG_RABBITMQ_IMG['queue'], durable=True )
	channel.basic_consume(
		queue=CONFIG_RABBITMQ_IMG['queue'], auto_ack=False,
		on_message_callback=lambda ch, method, props, body: callback( minio_client, ch, method, props, body )
	)
	print( "Consumer de imágenes iniciado" )

	try: channel.start_consuming( )
	except KeyboardInterrupt:
		rabbit_client.close( )
		sys.exit( 0 )


if __name__ == '__main__':
	main( )
