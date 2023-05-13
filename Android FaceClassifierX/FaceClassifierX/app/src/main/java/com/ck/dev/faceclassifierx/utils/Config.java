package com.ck.dev.faceclassifierx.utils;

import android.content.Context;
import android.util.DisplayMetrics;
import android.util.Log;

public class Config {

    public static final String TAG_SPLASH                = "message_activity_splash";
    public static final String TAG_CAMERA                = "message_camera_activity";
    public static final String TAG_OPEN_CV               = "message_open_cv";
    public static final String TAG_IMG_ANALYZER          = "message_img_analyzer";
    public static final String TAG_TF                    = "message_tensorflow";
    public static final String TAG_GENDER_CLASSIFICATION = "message_model_face_detection";

    public static final int TENSOR_FLOW_INPUT_SIZE = 128;
    public static final String MODEL_PATH = "model.tflite";
    public static final String LABEL_PATH = "labels.txt";

    public static final int FACE_DETECTION_LIMIT = 480;

    public static final int PERMISSION_REQUEST = 103;

    public static final String SUPPORTED_ABI = "arm64-v8a";

    public static boolean DEBUG_OFF = false;

    public static void LOG(String tag, String message, boolean error) {
        if (DEBUG_OFF) {
            return;
        }
        if (error) {
            Log.e(tag, message);
        } else {
            Log.d(tag, message);
        }
    }

    public static float convertDpToPixels(int dp, Context context) { return dp * ((float)context.getResources().getDisplayMetrics().densityDpi / DisplayMetrics.DENSITY_DEFAULT);}
}
