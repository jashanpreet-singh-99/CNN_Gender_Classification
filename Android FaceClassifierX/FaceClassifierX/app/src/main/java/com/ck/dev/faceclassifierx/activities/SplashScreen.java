package com.ck.dev.faceclassifierx.activities;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.widget.Toast;

import androidx.annotation.NonNull;

import com.ck.dev.faceclassifierx.R;
import com.ck.dev.faceclassifierx.utils.Config;

public class SplashScreen extends Activity {

    private final String[] permissionArray = new String[] {Manifest.permission.CAMERA};

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.layout_splash_screen);
        String ABI = Build.SUPPORTED_ABIS[0];
        Config.LOG(Config.TAG_SPLASH, "ABI Version : " + ABI, false);
        if (!ABI.equals(Config.SUPPORTED_ABI)) {
            Toast.makeText(getApplicationContext(), "ABI not supported.", Toast.LENGTH_LONG).show();
            return;
        }
        if (!checkPermissions()) {
            requestPermissions(permissionArray, Config.PERMISSION_REQUEST);
        } else {
            nextActivity();
        }
    }

    private boolean checkPermissions() {
        int PERMISSION_CAMERA = this.checkSelfPermission(Manifest.permission.CAMERA);
        Config.LOG(Config.TAG_SPLASH, "Permission for using camera : " + PERMISSION_CAMERA, false);
        return PERMISSION_CAMERA == PackageManager.PERMISSION_GRANTED;
    }

    private void nextActivity() {
        new Handler().postDelayed(() -> {
            startActivity(new Intent(getApplicationContext(), HomeScreen.class));
            finish();
        }, 1000);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        if (requestCode == Config.PERMISSION_REQUEST) {
            if (grantResults.length > 0) {
                boolean cameraReq = grantResults[0] == PackageManager.PERMISSION_GRANTED;
                if (cameraReq) {
                    nextActivity();
                } else {
                    requestPermissions(permissionArray, Config.PERMISSION_REQUEST);
                }
            }
        }
    }
}