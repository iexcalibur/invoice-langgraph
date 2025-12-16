"use client";

import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Upload, X, File } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface AttachmentUploadProps {
  attachments: string[];
  onChange: (attachments: string[]) => void;
  maxFiles?: number;
}

export function AttachmentUpload({
  attachments,
  onChange,
  maxFiles = 10,
}: AttachmentUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const handleFileSelect = (files: FileList | null) => {
    if (!files) return;

    const newFiles = Array.from(files).slice(0, maxFiles - attachments.length);
    const newAttachments = newFiles.map((file) => file.name);
    
    onChange([...attachments, ...newAttachments]);
    
    toast({
      title: "Files added",
      description: `${newAttachments.length} file(s) added`,
    });
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFileSelect(e.dataTransfer.files);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const removeAttachment = (index: number) => {
    onChange(attachments.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-4">
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isDragging
            ? "border-purple-500 bg-purple-500/10"
            : "border-purple-500/20 hover:border-purple-500/40"
        }`}
      >
        <Upload className="w-12 h-12 text-white/40 mx-auto mb-4" />
        <p className="text-white mb-2">
          Drag and drop files here, or{" "}
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="text-purple-400 hover:text-purple-300 underline"
          >
            browse
          </button>
        </p>
        <p className="text-sm text-white/60">
          Max {maxFiles} files (PDF, images, etc.)
        </p>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          className="hidden"
          onChange={(e) => handleFileSelect(e.target.files)}
        />
      </div>

      {attachments.length > 0 && (
        <div className="space-y-2">
          {attachments.map((attachment, index) => (
            <Card key={index} className="glass p-3 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <File className="w-5 h-5 text-white/60" />
                <span className="text-white">{attachment}</span>
              </div>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => removeAttachment(index)}
                className="text-red-400 hover:text-red-300"
              >
                <X className="w-4 h-4" />
              </Button>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

