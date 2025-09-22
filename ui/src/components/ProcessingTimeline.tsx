"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ProcessingEvent } from '@/lib/types';
import { Loader2, CheckCircle, AlertCircle, Brain, FileText, BarChart } from 'lucide-react';

interface ProcessingTimelineProps {
  events: ProcessingEvent[];
  isLoading: boolean;
}

export function ProcessingTimeline({ events, isLoading }: ProcessingTimelineProps) {
  const [collapsed, setCollapsed] = useState(false);

  const toggleCollapsed = () => setCollapsed((c) => !c);

  const getEventIcon = (event: ProcessingEvent) => {
    switch (event.type) {
      case 'agent_start':
        return <Brain className="h-6 w-6 text-blue-500" />;
      case 'agent_complete':
        return <CheckCircle className="h-6 w-6 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-6 w-6 text-red-500" />;
      case 'final':
        return <FileText className="h-6 w-6 text-purple-500" />;
      default:
        return <BarChart className="h-6 w-6 text-orange-500" />;
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
    <Card className="w-full max-w-6xl mx-auto">
      <CardHeader>
        <div className="flex items-center justify-between w-full">
          <div>
            <CardTitle className="flex items-center gap-2">
              {isLoading && <Loader2 className="h-6 w-6 animate-spin" />}
              Processing Timeline
            </CardTitle>
            <CardDescription>
              Real-time logs from the multi-agent processing workflow
            </CardDescription>
          </div>
          <div className="ml-4">
            <button
              aria-expanded={!collapsed}
              aria-controls="processing-timeline-content"
              onClick={toggleCollapsed}
              className="inline-flex items-center gap-2 px-3 py-1.5 rounded-md border bg-transparent text-sm hover:bg-muted/10"
            >
              {collapsed ? 'Expand' : 'Collapse'}
              <svg
                className={`h-4 w-4 transform ${collapsed ? '' : 'rotate-180'}`}
                viewBox="0 0 20 20"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path d="M5 8l5 5 5-5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div id="processing-timeline-content" className={`${collapsed ? 'hidden' : 'block'} max-h-[60vh] overflow-y-auto space-y-3 transition-all` }>
          {events.length === 0 && !isLoading ? (
            <div className="text-center py-8 text-muted-foreground">
              <BarChart className="h-16 w-16 mx-auto mb-2 opacity-50" />
              <p>No processing events yet</p>
            </div>
          ) : (
            <div className="space-y-2">
              {events.map((event, index) => (
                <div key={index} className="flex items-start gap-4 p-4 rounded-xl bg-muted/30">
                  <div className="flex-shrink-0 mt-1">
                    {getEventIcon(event)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className={`text-base font-semibold ${getEventColor(event)}`}>
                        {event.agentName ? `${event.agentName}` : event.type.replace('_', ' ').toUpperCase()}
                      </p>
                      <span className="text-sm text-muted-foreground">
                        {event.timestamp.toLocaleTimeString()}
                      </span>
                    </div>
                    <p className="text-base text-foreground mt-2 break-words">
                      {event.content}
                    </p>
                    {event.metadata && (
                      <div className="mt-3 text-sm text-muted-foreground">
                        <code className="bg-muted px-2 py-1 rounded block overflow-auto whitespace-pre-wrap">
                          {JSON.stringify(event.metadata, null, 2)}
                        </code>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/30">
                  <Loader2 className="h-6 w-6 animate-spin text-primary" />
                  <p className="text-base text-muted-foreground">Processing...</p>
                </div>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}