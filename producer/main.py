import os
import time

import cv2
import pika

# Configuración de RabbitMQ
CONFIG_RABBITMQ = {
	'url'     : '192.168.1.46:31702',
	'username': 'admin',
	'password': 'Admin@12345',
	'queue'   : 'images',
}


def try_catch_decorator ( func ):
	def wrapper ( *args, **kwargs ):
		try:
			return func( *args, **kwargs )
		except Exception as e:
			print( f"Error: {e}" )
			return None

	return wrapper


@try_catch_decorator
def connect_to_rabbitmq ( ):
	""" Conectar a RabbitMQ """
	connection = pika.BlockingConnection(
		pika.ConnectionParameters(
			host=CONFIG_RABBITMQ['url'].split( ':' )[0],
			port=int( CONFIG_RABBITMQ['url'].split( ':' )[1] ),
			credentials=pika.PlainCredentials( CONFIG_RABBITMQ['username'], CONFIG_RABBITMQ['password'] )
		)
	)
	channel = connection.channel( )
	channel.queue_declare( queue=CONFIG_RABBITMQ['queue'], durable=True )
	return channel, connection


@try_catch_decorator
def send_frame_to_rabbitmq ( channel, frame, frame_counter, video_file ):
	""" Envía un frame en formato binario a RabbitMQ """
	if frame is None or frame.size == 0:
		print( f"Frame vacío en {video_file}, frame {frame_counter}" )
		return

	success, buffer = cv2.imencode( '.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90] )
	if not success:
		print( f"Error al convertir frame {frame_counter} a JPG en {video_file}" )
		return

	frame_bytes = buffer.tobytes( )
	channel.basic_publish(
		exchange='',
		routing_key=CONFIG_RABBITMQ['queue'],
		body=frame_bytes,
	)
	print( f"Sent frame {frame_counter} from {video_file} to RabbitMQ" )


@try_catch_decorator
def video_stream_producer ( video_folder, fps=30 ):
	""" Lee los videos y envía los frames a RabbitMQ """
	channel, connection = connect_to_rabbitmq( )

	video_files = [f for f in os.listdir( video_folder ) if f.endswith( ('.mp4', '.avi') )]
	if not video_files:
		print( "No videos found in folder." )
		return

	for video_file in video_files:
		video_path = os.path.join( video_folder, video_file )
		cap = cv2.VideoCapture( video_path )

		if not cap.isOpened( ):
			print( f"Error opening video {video_file}" )
			continue

		frame_time = 1.0 / fps
		frame_counter = 0

		while True:
			ret, frame = cap.read( )
			if not ret:
				print( f"End of video {video_file}." )
				break

			frame_counter += 1
			send_frame_to_rabbitmq( channel, frame, frame_counter, video_file )
			time.sleep( frame_time )

		cap.release( )

	channel.close( )
	connection.close( )
	cv2.destroyAllWindows( )


if __name__ == "__main__":
	video_path = 'videos/'
	video_stream_producer( video_path )
