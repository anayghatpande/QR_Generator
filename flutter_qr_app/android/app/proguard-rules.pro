# ML Kit barcode scanning
-keep class com.google.mlkit.** { *; }
-keep class com.google.mlkit.vision.barcode.** { *; }
-keep class com.google.mlkit.vision.common.** { *; }
-keep class com.google.android.gms.vision.** { *; }
-keep class com.google.android.libraries.barhopper.** { *; }
-keep class com.google.photos.** { *; }

# CameraX
-keep class androidx.camera.** { *; }
-keep class androidx.camera.core.** { *; }
-keep class androidx.camera.lifecycle.** { *; }
-keep class androidx.camera.camera2.** { *; }

# AndroidX Lifecycle (used by CameraX)
-keep class androidx.lifecycle.** { *; }

# Flutter engine - prevent stripping of engine callbacks
-keep class io.flutter.** { *; }
-keep class io.flutter.embedding.engine.** { *; }
-keep class io.flutter.view.** { *; }

# Keep enum methods for mobile_scanner
-keepclassmembers class * extends java.lang.Enum {
    <fields>;
    public static **[] values();
    public static ** valueOf(java.lang.String);
}

# Keep all classes referenced by mobile_scanner plugin
-keep class dev.steenbakker.mobile_scanner.** { *; }
