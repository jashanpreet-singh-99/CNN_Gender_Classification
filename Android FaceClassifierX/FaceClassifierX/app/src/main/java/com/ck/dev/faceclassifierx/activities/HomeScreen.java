package com.ck.dev.faceclassifierx.activities;

import android.annotation.SuppressLint;
import android.content.res.ColorStateList;
import android.graphics.Bitmap;
import android.graphics.Rect;
import android.graphics.SurfaceTexture;
import android.hardware.camera2.CameraAccessException;
import android.hardware.camera2.CameraCharacteristics;
import android.hardware.camera2.CameraManager;
import android.hardware.camera2.params.StreamConfigurationMap;
import android.media.Image;
import android.os.Bundle;
import android.os.Vibrator;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.camera.core.Camera;
import androidx.camera.core.CameraControl;
import androidx.camera.core.CameraSelector;
import androidx.camera.core.ImageAnalysis;
import androidx.camera.core.ImageCapture;
import androidx.camera.core.Preview;
import androidx.camera.lifecycle.ProcessCameraProvider;
import androidx.camera.view.PreviewView;
import androidx.core.content.ContextCompat;

import com.ck.dev.faceclassifierx.R;
import com.ck.dev.faceclassifierx.classifier.GenderClassifier;
import com.ck.dev.faceclassifierx.interfaces.Classifier;
import com.ck.dev.faceclassifierx.utils.AnalyzerState;
import com.ck.dev.faceclassifierx.utils.Config;
import com.google.common.util.concurrent.ListenableFuture;
import com.google.mlkit.vision.common.InputImage;
import com.google.mlkit.vision.face.Face;
import com.google.mlkit.vision.face.FaceDetection;
import com.google.mlkit.vision.face.FaceDetector;
import com.google.mlkit.vision.face.FaceDetectorOptions;

import org.opencv.android.OpenCVLoader;
import org.opencv.android.Utils;
import org.opencv.core.Core;
import org.opencv.core.CvType;
import org.opencv.core.Mat;
import org.opencv.core.Point;
import org.opencv.core.Scalar;
import org.opencv.core.Size;
import org.opencv.imgproc.Imgproc;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;

public class HomeScreen extends AppCompatActivity {

    private PreviewView cameraView;
    private ImageButton captureBtn;
    private ImageButton switchCameraBtn;
    private ImageButton settingsBtn;
    private ImageView semiView;

    private LinearLayout settingsLayout;
    private ImageButton  settingsCloseBtn;
    private Button       flashBtn;
    private LinearLayout outputResolutionView;

    private final Executor executor = Executors.newSingleThreadExecutor();
    private final Executor executorTf = Executors.newSingleThreadExecutor();

    private Classifier classifier;
    
    private FaceDetector detector;

    private AnalyzerState analyzerState = AnalyzerState.STOPPED;

    private ProcessCameraProvider cameraProvider;

    private int lensFacing = CameraSelector.LENS_FACING_BACK;
    private CameraControl cameraControl;

    private android.util.Size[] cameraOuts;

    private boolean flash = false;

    private Vibrator vibrator;

    private int resolutionIndex = 0;
    private int resolutionBtnIndex = 0;

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.layout_home_screen);
        if (!OpenCVLoader.initDebug())
            Config.LOG(Config.TAG_OPEN_CV, "Unable to load OpenCV", true);
        else
            Config.LOG(Config.TAG_OPEN_CV, "OpenCV loaded", false);
        initTensorFlow();
        initFaceDetector();
        initView();
    }

    private void initFaceDetector() {
        FaceDetectorOptions options = new FaceDetectorOptions.Builder()
                .setContourMode(FaceDetectorOptions.CONTOUR_MODE_ALL)
                .build();
        detector = FaceDetection.getClient(options);
    }

    private void initView() {
        cameraView      = this.findViewById(R.id.camera_view);
        captureBtn      = this.findViewById(R.id.capture_btn);
        switchCameraBtn = this.findViewById(R.id.switch_camera);
        settingsBtn     = this.findViewById(R.id.settings_btn);
        semiView        = this.findViewById(R.id.semi_preview);

        settingsLayout   = this.findViewById(R.id.settings_layout);
        settingsCloseBtn = this.findViewById(R.id.close_dialog_btn);
        flashBtn         = this.findViewById(R.id.flash_btn);

        outputResolutionView = this.findViewById(R.id.out_resolution_view);

        vibrator = (Vibrator) getApplicationContext().getSystemService(VIBRATOR_SERVICE);

        startCamera();

        onClick();
    }

    private void onClick() {
        captureBtn.setOnClickListener(v -> {
            vibrator.vibrate(100);
            if (analyzerState.equals(AnalyzerState.STOPPED)) {
                analyzerState = AnalyzerState.PROCESSING;
                captureBtn.setImageDrawable(ContextCompat.getDrawable(this, R.drawable.ic_cancel));
            } else {
                analyzerState = AnalyzerState.STOPPED;
                captureBtn.setImageDrawable(ContextCompat.getDrawable(this, R.drawable.ic_camera));
            }
        });

        switchCameraBtn.setOnClickListener(v -> {
            vibrator.vibrate(100);
            if (lensFacing == CameraSelector.LENS_FACING_BACK) {
                lensFacing = CameraSelector.LENS_FACING_FRONT;
                switchCameraBtn.setImageDrawable(ContextCompat.getDrawable(this, R.drawable.ic_camera_rear));
            } else {
                lensFacing = CameraSelector.LENS_FACING_BACK;
                switchCameraBtn.setImageDrawable(ContextCompat.getDrawable(this, R.drawable.ic_camera_front));
            }
            bindPreview();
        });

        flashBtn.setOnClickListener( v -> {
            vibrator.vibrate(100);
            if ( cameraControl != null ) {
                flash = !flash;
                if (flash) {
                    flashBtn.setText(R.string.on);
                    flashBtn.setBackgroundTintList(ColorStateList.valueOf(ContextCompat.getColor(getApplicationContext(), R.color.purple_500)));
                } else {
                    flashBtn.setText(R.string.off);
                    flashBtn.setBackgroundTintList(ColorStateList.valueOf(ContextCompat.getColor(getApplicationContext(), R.color.black_600)));
                }
                cameraControl.enableTorch(flash);
            }
        });

        settingsBtn.setOnClickListener( v -> {
            vibrator.vibrate(100);
            if (settingsLayout.getVisibility() == View.GONE) {
                settingsLayout.setVisibility(View.VISIBLE);
            }
        });

        settingsCloseBtn.setOnClickListener( v -> {
            vibrator.vibrate(100);
            if (settingsLayout.getVisibility() == View.VISIBLE) {
                settingsLayout.setVisibility(View.GONE);
            }
        });
    }

    private void startCamera() {
        final ListenableFuture<ProcessCameraProvider> cameraProviderFuture = ProcessCameraProvider.getInstance(this);

        cameraProviderFuture.addListener(() -> {
            try {
                cameraProvider = cameraProviderFuture.get();
                bindPreview(cameraProvider);
            } catch (Exception e) {
                Config.LOG(Config.TAG_CAMERA, "Unable to start camera. " + e.getMessage(), true);
            }
        }, ContextCompat.getMainExecutor(this));
    }

    private void bindPreview() {
        bindPreview(cameraProvider);
    }

    private void bindPreview(ProcessCameraProvider cameraProvider) {
        cameraProvider.unbindAll();
        getSupportedResolutions();
        if (cameraOuts.length < 1) {
            return;
        }
        android.util.Size outResolution = new android.util.Size(cameraOuts[resolutionIndex].getHeight(), cameraOuts[resolutionIndex].getWidth());
        Preview preview = new Preview.Builder().setTargetResolution(outResolution).build();

        CameraSelector cameraSelector = new CameraSelector.Builder().requireLensFacing(lensFacing).build();

        ImageAnalysis imageAnalysis = new ImageAnalysis.Builder().setTargetResolution(outResolution).setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST).build();
        imageAnalysis.setAnalyzer(executor, image -> {
            long startTime = System.nanoTime();
            @SuppressLint("UnsafeExperimentalUsageError") Image img = image.getImage();
            if (img != null && analyzerState.equals(AnalyzerState.PROCESSING)) {
                Mat mat = convertYUVtoMat(img);
                Mat retFrame = new Mat(mat.rows(), mat.cols(), CvType.CV_8UC4, new Scalar(0, 0, 0, 0));
                InputImage inputImage = InputImage.fromMediaImage(img, image.getImageInfo().getRotationDegrees());
                detector.process(inputImage).addOnSuccessListener(faces -> {
                    Config.LOG(Config.TAG_IMG_ANALYZER, "Faces Detected : " + faces.size(), false);

                    for (Face face : faces) {
                        Rect bounds = face.getBoundingBox();
                        int element = Math.min(bounds.width(), bounds.height());

                        int startX = bounds.centerX() - element;
                        int endX   = bounds.centerX() + element;

                        if (startX < 0)
                            startX = 0;
                        if (endX > img.getHeight())
                            endX = img.getHeight();

                        int startY = bounds.centerY() - element;
                        int endY   = bounds.centerY() + element;

                        if (startY < 0)
                            startY = 0;
                        if (endY > img.getWidth())
                            endY = img.getWidth();

                        Imgproc.rectangle(retFrame, new Point(startX, startY), new Point(endX, endY), new Scalar(0, 255, 0, 255));

                        Mat cropped = new Mat(mat, new org.opencv.core.Rect(new Point(startX, startY), new Point(endX, endY)));
                        Mat resized = new Mat();
                        Imgproc.resize(cropped, resized, new Size(Config.TENSOR_FLOW_INPUT_SIZE, Config.TENSOR_FLOW_INPUT_SIZE));
                        try {
                            final List<Classifier.Recognition> results = classifier.recognizeImage(resized);
                            Config.LOG(Config.TAG_GENDER_CLASSIFICATION, "RESULT OF CLASSIFICATION MAT : " + results.toString(), false);

                            String label =  results.get(0) + "";
                            int[] baseLine = new int[1];
                            Size labelSize = Imgproc.getTextSize(label, Imgproc.FONT_HERSHEY_SIMPLEX, 0.5, 1, baseLine);
                            Imgproc.rectangle(retFrame, new Point(startX, startY - labelSize.height), new Point(startX + labelSize.width, startY + baseLine[0]), new Scalar(255, 255, 255, 255), Imgproc.FILLED);
                            Imgproc.putText(retFrame, label, new Point(startX, startY), Imgproc.FONT_HERSHEY_SIMPLEX, 0.5, new Scalar(0, 0, 0, 255));
                        } catch (Exception e) {
                            Config.LOG(Config.TAG_GENDER_CLASSIFICATION , "Error in classification " + e, false);
                        }
                        if (faces.size() > 0) {
                            Bitmap bitmap = Bitmap.createBitmap(retFrame.cols(), retFrame.rows(), Bitmap.Config.ARGB_8888);
                            Utils.matToBitmap(retFrame, bitmap);
                            runOnUiThread(() -> semiView.setImageBitmap(bitmap));
                        }
                    }
                }).addOnCompleteListener(task -> {
                    if (task.getResult().size() == 0) {
                        runOnUiThread(() -> semiView.setImageBitmap(null));
                    }
                    image.close();
                    Config.LOG(Config.TAG_IMG_ANALYZER, "# : Timed : " + (System.nanoTime() - startTime)/1000000 + " mS", false);
                });
            } else {
                runOnUiThread(() -> semiView.setImageBitmap(null));
                image.close();
                Config.LOG(Config.TAG_IMG_ANALYZER, "# : Timed : " + (System.nanoTime() - startTime)/1000000 + " mS", false);
            }
        });

        ImageCapture.Builder imageCaptureBuilder = new ImageCapture.Builder().setTargetResolution(outResolution);

        final ImageCapture imageCapture;
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.R) {
            imageCapture = imageCaptureBuilder.setTargetRotation(this.getDisplay().getRotation()).build();
        } else {
            imageCapture = imageCaptureBuilder.setTargetRotation(this.getWindowManager().getDefaultDisplay().getRotation()).build();
        }

        preview.setSurfaceProvider(cameraView.getSurfaceProvider());

        Camera camera = cameraProvider.bindToLifecycle(this, cameraSelector, preview, imageAnalysis, imageCapture);
        cameraControl = camera.getCameraControl();
        cameraControl.enableTorch(flash);
    }

    private void getSupportedResolutions() {
        CameraManager cameraManager = (CameraManager) getApplicationContext().getSystemService(CAMERA_SERVICE);
        try {
            CameraCharacteristics cameraCharacteristics = cameraManager.getCameraCharacteristics(lensFacing + "");
            StreamConfigurationMap streamConfigurationMap = cameraCharacteristics.get((CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP));
            cameraOuts = streamConfigurationMap.getOutputSizes(SurfaceTexture.class);
            if (cameraOuts.length > 0) {
                int child = 0;
                outputResolutionView.removeAllViews();
                LayoutInflater layoutInflater = (LayoutInflater) getApplication().getSystemService(LAYOUT_INFLATER_SERVICE);
                LinearLayout.LayoutParams layoutParams = new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
                int pixels = (int) Config.convertDpToPixels(10, getApplicationContext());
                layoutParams.setMargins(pixels, pixels/2, pixels, pixels/2);
                for (int i = 0 ; i < cameraOuts.length; i++) {
                    android.util.Size size = cameraOuts[i];
                    Config.LOG(Config.TAG_CAMERA, "Supported Resolutions : " + size.getWidth() + "x" + size.getHeight(), false);
                    if (size.getWidth() < Config.FACE_DETECTION_LIMIT || size.getHeight() < Config.FACE_DETECTION_LIMIT) {
                        continue;
                    }
                    @SuppressLint("InflateParams") TextView textView = (TextView) layoutInflater.inflate(R.layout.item_resolution_selection, null);
                    textView.setText(String.format(Locale.ENGLISH, "%dx%d", cameraOuts[i].getWidth(), cameraOuts[i].getHeight()));
                    textView.setTag(i);
                    if (child == resolutionBtnIndex) {
                        textView.setBackgroundTintList(ColorStateList.valueOf(ContextCompat.getColor(getApplicationContext(), R.color.purple_500)));
                    } else {
                        textView.setBackgroundTintList(ColorStateList.valueOf(ContextCompat.getColor(getApplicationContext(), R.color.black_600)));
                    }
                    textView.setOnClickListener( v -> {
                        TextView prevTxt = (TextView) outputResolutionView.getChildAt(resolutionBtnIndex);
                        prevTxt.setBackgroundTintList(ColorStateList.valueOf(ContextCompat.getColor(getApplicationContext(), R.color.black_600)));
                        resolutionIndex = (int) v.getTag();
                        resolutionBtnIndex = outputResolutionView.indexOfChild(v);
                        v.setBackgroundTintList(ColorStateList.valueOf(ContextCompat.getColor(getApplicationContext(), R.color.purple_500)));
                        bindPreview();
                    });
                    textView.setLayoutParams(layoutParams);
                    outputResolutionView.addView(textView, child);
                    child++;
                }
            }

        } catch (CameraAccessException e) {
            Config.LOG(Config.TAG_CAMERA, "Unable to get selected Camera's resolution details.", true);
        }
    }

    private Mat convertYUVtoMat(@NonNull Image img) {
        byte[] nv21;

        ByteBuffer yBuffer = img.getPlanes()[0].getBuffer();
        ByteBuffer uBuffer = img.getPlanes()[1].getBuffer();
        ByteBuffer vBuffer = img.getPlanes()[2].getBuffer();

        int ySize = yBuffer.remaining();
        int uSize = uBuffer.remaining();
        int vSize = vBuffer.remaining();

        nv21 = new byte[ySize + uSize + vSize];

        yBuffer.get(nv21, 0, ySize);
        vBuffer.get(nv21, ySize, vSize);
        uBuffer.get(nv21, ySize + vSize, uSize);

        Mat yuv = new Mat(img.getHeight() + img.getHeight()/2, img.getWidth(), CvType.CV_8UC1);
        yuv.put(0, 0, nv21);
        Mat rgb = new Mat();
        Imgproc.cvtColor(yuv, rgb, Imgproc.COLOR_YUV2GRAY_NV21, 1);
        Core.rotate(rgb, rgb, Core.ROTATE_90_CLOCKWISE);
        return  rgb;
    }

    private void initTensorFlow() {
        Config.LOG(Config.TAG_TF, "Classifier Ready.", false);
        executorTf.execute(() -> {
            try {
                classifier = GenderClassifier.create(
                        getAssets(),
                        Config.MODEL_PATH,
                        Config.LABEL_PATH,
                        Config.TENSOR_FLOW_INPUT_SIZE,
                        true
                );
                Config.LOG(Config.TAG_TF, "Classifier Ready.", false);
            } catch (IOException e) {
                Config.LOG(Config.TAG_TF, "Classifier Error : " + e.getMessage(), false);
            }
        });
    }
}
