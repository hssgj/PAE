package cz.pae.mobile;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.TextView;

public class MainActivity extends Activity {
    private static final String URL = "http://127.0.0.1:8765/";
    private final Handler handler = new Handler(Looper.getMainLooper());
    private WebView webView;
    private TextView status;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        status = new TextView(this);
        status.setText("Spouštím PAE v Termuxu…");
        status.setTextColor(Color.WHITE);
        status.setBackgroundColor(Color.rgb(16, 19, 26));
        status.setGravity(android.view.Gravity.CENTER);
        status.setTextSize(18);
        setContentView(status);
        startPae();
        handler.postDelayed(this::openChat, 1200);
    }

    private void startPae() {
        Intent intent = new Intent("com.termux.RUN_COMMAND");
        intent.setClassName("com.termux", "com.termux.app.RunCommandService");
        intent.putExtra("com.termux.RUN_COMMAND_PATH", "/data/data/com.termux/files/usr/bin/bash");
        intent.putExtra("com.termux.RUN_COMMAND_ARGUMENTS", new String[]{"/data/data/com.termux/files/home/PAE/start-mobile.sh"});
        intent.putExtra("com.termux.RUN_COMMAND_WORKDIR", "/data/data/com.termux/files/home/PAE");
        intent.putExtra("com.termux.RUN_COMMAND_BACKGROUND", true);
        try {
            startService(intent);
        } catch (Exception error) {
            status.setText("Termux PAE nejde spustit. Povol aplikaci PAE oprávnění Run commands.");
        }
    }

    private void openChat() {
        webView = new WebView(this);
        webView.setBackgroundColor(Color.rgb(16, 19, 26));
        webView.getSettings().setJavaScriptEnabled(true);
        webView.getSettings().setDomStorageEnabled(true);
        webView.setWebChromeClient(new WebChromeClient());
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageFinished(WebView view, String url) {
                handler.removeCallbacksAndMessages(null);
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (request.isForMainFrame()) {
                    handler.postDelayed(() -> view.loadUrl(URL), 1500);
                }
            }
        });
        setContentView(webView);
        webView.loadUrl(URL);
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) webView.goBack();
        else super.onBackPressed();
    }
}
