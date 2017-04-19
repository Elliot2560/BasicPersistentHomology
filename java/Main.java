import comp.BarcodeComputer;
import edu.stanford.math.plex4.homology.barcodes.BarcodeCollection;
import io.FileIO;

import java.io.IOException;

/**
 * Created by elliot on 3/28/17.
 */
public class Main {

    public static void main(String[] args) throws IOException {

        // Parameters for javaplex
        String inputFile = "../data/in/iris.in";
        String outputFile = "../data/out/iris.out";
        int characteristic = 0;
        int numLandmarkPoints = 100;
        int maxDimension = 2;
        double filtrationRatio = 0.4;
        int numDivisions = 20;

        double[][] points = FileIO.getPointsFromFile(inputFile);

        BarcodeCollection<Double> intervals = BarcodeComputer.landmarkCalculate(points, characteristic, numLandmarkPoints, maxDimension, filtrationRatio, numDivisions);
        FileIO.writeBarcodeToFile(intervals, outputFile);

        System.out.println("Run successful!");

    }

}
