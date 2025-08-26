package com.example.wiremock;

import com.github.tomakehurst.wiremock.extension.Parameters;
import com.github.tomakehurst.wiremock.extension.ResponseTransformer;
import com.github.tomakehurst.wiremock.http.Request;
import com.github.tomakehurst.wiremock.http.Response;
import com.github.tomakehurst.wiremock.http.ResponseDefinition;

import java.util.HashMap;
import java.util.Map;

public class OutgoingRequestLogger extends ResponseTransformer {

    @Override
    public Response transform(Request request, Response response, ResponseDefinition responseDefinition, Parameters parameters) {
        Map<String, Object> logEntry = new HashMap<>();
        logEntry.put("method", request.getMethod().value());
        logEntry.put("url", request.getUrl());
        logEntry.put("headers", request.getHeaders().all());
        logEntry.put("body", request.getBodyAsString());

        System.out.println("=== Outgoing Request ===");
        System.out.println(logEntry);

        return response; // Don’t modify the response, just log
    }

    @Override
    public String getName() {
        return "outgoing-request-logger";
    }

    @Override
    public boolean applyGlobally() {
        return true; // Apply to all requests
    }
}