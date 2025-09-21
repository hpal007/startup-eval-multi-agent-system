"use client";

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ProcessingEvent } from '@/lib/types';
import { Loader2, CheckCircle, AlertCircle, Brain, FileText, BarChart } from 'lucide-react';

interface ProcessingTimelineProps {
  events: ProcessingEvent[];
  isLoading: boolean;
}

export function ProcessingTimeline({ events, isLoading }: ProcessingTimelineProps) {
  const getEventIcon = (event: ProcessingEvent) => {
    switch (event.type) {
      case 'agent_start':
        return <Brain className="h-4 w-4 text-blue-500" />;
      case 'agent_complete':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      case 'final':
        return <FileText className="h-4 w-4 text-purple-500" />;
      default:
        return <BarChart className="h-4 w-4 text-orange-500" />;
    }
  };

  const getEventColor = (event: ProcessingEvent) => {
    switch (event.type) {
      case 'agent_start':
        return 'text-blue-400';
      case 'agent_complete':
        return 'text-green-400';
      case 'error':
        return 'text-red-400';
      case 'final':
        return 'text-purple-400';
      default:
        return 'text-orange-400';
    }
  };

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {isLoading && <Loader2 className="h-5 w-5 animate-spin" />}
          Processing Timeline
        </CardTitle>
        <CardDescription>
          Real-time logs from the multi-agent processing workflow
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="max-h-96 overflow-y-auto space-y-3">
          {events.length === 0 && !isLoading ? (
            <div className="text-center py-8 text-muted-foreground">
              <BarChart className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p>No processing events yet</p>
            </div>
          ) : (
            <div className="space-y-2">
              {events.map((event, index) => (
                <div key={index} className="flex items-start gap-3 p-3 rounded-lg bg-muted/30">
                  <div className="flex-shrink-0 mt-0.5">
                    {getEventIcon(event)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className={`text-sm font-medium ${getEventColor(event)}`}>
                        {event.agentName ? `${event.agentName}` : event.type.replace('_', ' ').toUpperCase()}
                      </p>
                      <span className="text-xs text-muted-foreground">
                        {event.timestamp.toLocaleTimeString()}
                      </span>
                    </div>
                    <p className="text-sm text-foreground mt-1 break-words">
                      {event.content}
                    </p>
                    {event.metadata && (
                      <div className="mt-2 text-xs text-muted-foreground">
                        <code className="bg-muted px-2 py-1 rounded">
                          {JSON.stringify(event.metadata, null, 2)}
                        </code>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/30">
                  <Loader2 className="h-4 w-4 animate-spin text-primary" />
                  <p className="text-sm text-muted-foreground">Processing...</p>
                </div>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}