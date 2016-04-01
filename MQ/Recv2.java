import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.Channel;
import com.rabbitmq.client.AMQP;
import com.rabbitmq.client.Envelope;
import com.rabbitmq.client.Consumer;
import com.rabbitmq.client.DefaultConsumer;
import java.io.IOException;

public class Recv2{
	private static String QUEUE_NAME = "task_queue";

	public static void main(String[] args) throws Exception{
		ConnectionFactory factory = new ConnectionFactory();
		factory.setHost("localhost");
		final Connection connection = factory.newConnection();
		final Channel channel = connection.createChannel();

		channel.queueDeclare(QUEUE_NAME, true, false, false, null);
		System.out.println(" [*] waiting for messages, press CTRL+C to exit!");

         channel.basicQos(1);

	    final Consumer consumer = new DefaultConsumer(channel){
            @Override
            public void handleDelivery(String consumerTag, Envelope envelope, AMQP.BasicProperties properties, byte[] body) throws IOException{
            	String message = new String(body, "UTF-8");
            	System.out.println(" [x] Received '" + message + "'");
            	try{
            		doWork(message);

            	}finally{
            		System.out.println(" [x] Done");
            		channel.basicAck(envelope.getDeliveryTag(), false);
            	}

            }
        };
        channel.basicConsume(QUEUE_NAME, false, consumer);
	}

	private static void doWork(String task){
		try{
		    for(char ch: task.toCharArray()){
			    if(ch == '.') Thread.sleep(1000);
		    }
		}catch(InterruptedException e){
		}

	}
}