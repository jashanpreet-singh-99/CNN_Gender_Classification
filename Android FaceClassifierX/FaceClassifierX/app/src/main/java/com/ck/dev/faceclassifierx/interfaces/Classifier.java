package com.ck.dev.faceclassifierx.interfaces;

import androidx.annotation.NonNull;

import org.opencv.core.Mat;

import java.util.List;

public interface Classifier {

    class Recognition {

        String id;
        String title;
        Float confidence;
        boolean quant;

        public Float getConfidence() {
            return confidence;
        }

        public Recognition(String id, String title, Float confidence, boolean quant) {
            this.id = id;
            this.title = title;
            this.confidence = confidence;
            this.quant = quant;
        }

        @NonNull
        @Override
        public String toString() {
            String returnString = "";
            if (id != null) {
                returnString += "[" + id + "} ";
            }
            if (title != null) {
                returnString += title + " : ";
            }
            if (confidence != null) {
                returnString += confidence;
            }
            return returnString.trim();
        }
    }

    List<Recognition> recognizeImage(Mat mat);

}
