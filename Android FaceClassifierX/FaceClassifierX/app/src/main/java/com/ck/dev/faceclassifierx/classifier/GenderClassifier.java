package com.ck.dev.faceclassifierx.classifier;

import android.content.res.AssetFileDescriptor;
import android.content.res.AssetManager;

import com.ck.dev.faceclassifierx.interfaces.Classifier;
import com.ck.dev.faceclassifierx.utils.Config;

import org.opencv.core.Mat;
import org.tensorflow.lite.Interpreter;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.channels.FileChannel;
import java.util.ArrayList;
import java.util.List;
import java.util.PriorityQueue;

public class GenderClassifier implements Classifier {

    private Interpreter interpreter;
    private int inputSize;
    private List<String> labelList;
    private boolean quant;


    private static  final int MAX_RESULT = 2;

    public GenderClassifier() {
    }

    public static Classifier create(AssetManager assetManager, String modelPath, String labelPath, int inputSize, boolean quant) throws IOException {
        GenderClassifier classifier = new GenderClassifier();
        classifier.interpreter = new Interpreter(classifier.loadModelFile(assetManager, modelPath), new Interpreter.Options());
        classifier.labelList = classifier.loadLabelList(assetManager, labelPath);
        classifier.inputSize = inputSize;
        classifier.quant = quant;
        return classifier;
    }

    private List<String> loadLabelList(AssetManager assetManager, String labelPath) throws IOException {
        List<String> labelList = new ArrayList<>();
        BufferedReader reader = new BufferedReader(new InputStreamReader(assetManager.open(labelPath)));
        String line;
        while ((line = reader.readLine()) != null) {
            labelList.add(line);
        }
        reader.close();
        return labelList;
    }

    private ByteBuffer loadModelFile(AssetManager assetManager, String modelPath) throws IOException {
        AssetFileDescriptor fileDescriptor = assetManager.openFd(modelPath);
        FileInputStream inputStream = new FileInputStream(fileDescriptor.getFileDescriptor());
        FileChannel fileChannel = inputStream.getChannel();
        long startOffset = fileDescriptor.getStartOffset();
        long declaredLength = fileDescriptor.getDeclaredLength();
        return fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength);
    }

    @Override
    public List<Recognition> recognizeImage(Mat mat) {
        ByteBuffer byteBuffer = convertMatToByteBuffer(mat);
        float[][] result = new float[1][labelList.size()];
        interpreter.run(byteBuffer, result);
        for (int i = 0 ; i < labelList.size(); i++) {
            Config.LOG(Config.TAG_GENDER_CLASSIFICATION, " Results :" + labelList.get(i) + " " + result[0][i], false);
        }
        return getSortedResultByte(result);
    }

    private List<Recognition> getSortedResultByte(float[][] result) {
        PriorityQueue<Recognition> priorityQueue = new PriorityQueue<>(MAX_RESULT, (o1, o2) -> Float.compare(o2.getConfidence(), o1.getConfidence()));
        for (int i = 0; i < labelList.size(); i++) {
            float confidence = (result[0][i]);
            priorityQueue.add(new Classifier.Recognition("" + i, labelList.size() > 1 ? labelList.get(i) : "unknown", confidence, quant));
        }

        final ArrayList<Recognition> recognitions = new ArrayList<>();
        int recognitionSize = Math.min(priorityQueue.size(), MAX_RESULT);
        for (int i = 0; i < recognitionSize; i++) {
            recognitions.add(priorityQueue.poll());
        }
        return  recognitions;
    }

    private ByteBuffer convertMatToByteBuffer(Mat mat) {
        ByteBuffer byteBuffer;

        int modelInputSize = 4 * inputSize * inputSize;

        byteBuffer = ByteBuffer.allocateDirect(modelInputSize);
        byteBuffer.order(ByteOrder.nativeOrder());

        for (int i = 0 ; i < inputSize; i++) {
            for (int j = 0; j < inputSize; j++) {
                byteBuffer.putFloat((float)mat.get(i,j)[0]/255.0f);
            }
        }
        return  byteBuffer;
    }

}
