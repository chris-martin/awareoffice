package awareoffice;

import java.io.IOException;

import com.phidgets.Phidget;
import com.phidgets.PhidgetException;
import com.phidgets.TemperatureSensorPhidget;
import com.phidgets.event.AttachEvent;
import com.phidgets.event.AttachListener;
import com.phidgets.event.DetachEvent;
import com.phidgets.event.DetachListener;
import com.phidgets.event.ErrorEvent;
import com.phidgets.event.ErrorListener;
import com.phidgets.event.TemperatureChangeEvent;
import com.phidgets.event.TemperatureChangeListener;

public class Sensor {

    public static void main(String[] args) throws PhidgetException, IOException {
        System.out.println(Phidget.getLibraryVersion());


        final TemperatureSensorPhidget tempsensor = new TemperatureSensorPhidget();
        tempsensor.addAttachListener(new AttachListener() {
            public void attached(AttachEvent ae) {
                System.out.println("attachment of " + ae);
            }
        });
        tempsensor.addDetachListener(new DetachListener() {
            public void detached(DetachEvent ae) {
                System.out.println("detachment of " + ae);
            }
        });
        tempsensor.addErrorListener(new ErrorListener() {
            public void error(ErrorEvent ee) {
                System.out.println("error event for " + ee);
            }
        });
        tempsensor.addTemperatureChangeListener(new TemperatureChangeListener()
        {
            public void temperatureChanged(TemperatureChangeEvent oe)
            {
                try {
                    System.out.println(oe + ", Ambient temperature: " + tempsensor.getAmbientTemperature());
                } catch (PhidgetException e) {
                    System.err.println(e);
                }
            }
        });

        tempsensor.openAny();
        System.out.println("waiting for TemperatureSensor attachment...");
        tempsensor.waitForAttachment();

        System.out.println("Serial: " + tempsensor.getSerialNumber());
        tempsensor.setTemperatureChangeTrigger(0, 0.1);
        System.out.println("trigger: " + tempsensor.getTemperatureChangeTrigger(0));
        System.out.println("Outputting events.  Input to stop.");
        System.in.read();
        System.out.print("closing...");
        tempsensor.close();
        System.out.println(" ok");
        if (false) {
            System.out.println("wait for finalization...");
            System.gc();
        }
    }
}
