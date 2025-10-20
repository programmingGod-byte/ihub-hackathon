package com.finalagain;

import com.facebook.react.ReactActivity;
import com.facebook.react.ReactActivityDelegate;
import com.facebook.react.defaults.DefaultNewArchitectureEntryPoint;
import com.facebook.react.defaults.DefaultReactActivityDelegate;
import android.os.Bundle; // <- import this

public class MainActivity extends ReactActivity {

  @Override
  protected String getMainComponentName() {
    return "finalAgain";
  }

  @Override
  protected ReactActivityDelegate createReactActivityDelegate() {
    return new DefaultReactActivityDelegate(
        this,
        getMainComponentName(),
        DefaultNewArchitectureEntryPoint.getFabricEnabled());
  }

  // <<< ADD THIS METHOD
  @Override
  protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(null); // Important for Reanimated and TurboModules
  }
}
