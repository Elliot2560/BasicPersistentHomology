package io;

import edu.stanford.math.plex4.homology.barcodes.BarcodeCollection;
import edu.stanford.math.plex4.io.DoubleArrayReaderWriter;

import java.io.*;
import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * Created by elliot on 3/28/17.
 */
public class FileIO {

    public static double[][] getPointsFromFile(String filename) throws IOException {

        Path filepath = Paths.get(filename);
        DoubleArrayReaderWriter readerWriter = DoubleArrayReaderWriter.getInstance();
        double[][] points = readerWriter.importFromFile(filepath.toString());

        return points;

    }

    public static void writeBarcodeToFile(BarcodeCollection<Double> intervals, String filepath) throws IOException {

        BufferedWriter out = null;
        try {
            File file = new File(filepath);
            if (!file.exists()) {
                file.createNewFile();
            }
            FileWriter fStream = new FileWriter(file, false);
            out = new BufferedWriter(fStream);
            out.write(intervals.toString());
        } catch (IOException x) {
            System.err.println(x);
        } finally {
            if (out != null) {
                out.close();
            }
        }

    }

}
