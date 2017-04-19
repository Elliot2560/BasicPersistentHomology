package comp;

import edu.stanford.math.plex4.api.Plex4;
import edu.stanford.math.plex4.homology.barcodes.BarcodeCollection;
import edu.stanford.math.plex4.homology.chain_basis.Simplex;
import edu.stanford.math.plex4.homology.interfaces.AbstractPersistenceAlgorithm;
import edu.stanford.math.plex4.metric.landmark.LandmarkSelector;
import edu.stanford.math.plex4.streams.impl.LazyWitnessStream;
import edu.stanford.math.plex4.streams.impl.WitnessStream;

/**
 * Created by elliot on 3/28/17.
 */
public class BarcodeComputer {

    public static BarcodeCollection<Double> landmarkCalculate(double[][] points, int characteristic, int numLandmarkPoints, int maxDimension, double filtrationRatio, int numDivisions) {

        LandmarkSelector<double[]> landmarkSelector = Plex4.createMaxMinSelector(points, numLandmarkPoints);

        double maxDistance = landmarkSelector.getMaxDistanceFromPointsToLandmarks();
        double maxFiltrationValue = maxDistance * filtrationRatio;

        WitnessStream<double[]> stream = Plex4.createWitnessStream(landmarkSelector, maxDimension, maxFiltrationValue, numDivisions);
        stream.finalizeStream();

        AbstractPersistenceAlgorithm<Simplex> algorithm;
        if (characteristic == 0) {
            algorithm = Plex4.getDefaultSimplicialAlgorithm(maxDimension);
        } else {
            algorithm = Plex4.getModularSimplicialAlgorithm(maxDimension, characteristic);
        }

        BarcodeCollection<Double> intervals = algorithm.computeIntervals(stream);

        return intervals;

    }

    public static BarcodeCollection<Double> landmarkLazyCalculate(double[][] points, int characteristic, int numLandmarkPoints, int maxDimension, int numDivisions, double filtrationRatio) {

        LandmarkSelector<double[]> landmarkSelector = Plex4.createMaxMinSelector(points, numLandmarkPoints);

        double maxDistance = landmarkSelector.getMaxDistanceFromPointsToLandmarks();
        double maxFiltrationValue = maxDistance * filtrationRatio;

        LazyWitnessStream<double[]> stream = Plex4.createLazyWitnessStream(landmarkSelector, maxDimension, maxFiltrationValue, numDivisions);
        stream.finalizeStream();

        AbstractPersistenceAlgorithm<Simplex> algorithm;
        if (characteristic == 0) {
            algorithm = Plex4.getDefaultSimplicialAlgorithm(maxDimension);
        } else {
            algorithm = Plex4.getModularSimplicialAlgorithm(maxDimension, characteristic);
        }

        BarcodeCollection<Double> intervals = algorithm.computeIntervals(stream);

        return intervals;

    }

}
