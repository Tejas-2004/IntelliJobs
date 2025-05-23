"use client";
import { useState, useEffect, useRef } from "react";
import { useUser } from "@clerk/nextjs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Upload, CheckCircle, AlertCircle } from "lucide-react";
import io from "socket.io-client";

export default function UploadResume({ onUploadSuccess }) {
  const { user } = useUser();
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [error, setError] = useState("");
  const [progress, setProgress] = useState(0);

  const socketRef = useRef(null);

  useEffect(() => {
    if (!user?.id) return;

    if (!socketRef.current) {
      socketRef.current = io("http://localhost:5000/resume");
    }

    const socket = socketRef.current;

    socket.on("resume_progress", (data) => {
      if (data.userId === user.id) {
        setProgress(data.progress);
        if (data.progress >= 100) {
          setUploadStatus("success");
          setIsUploading(false);
          // Call the success callback to refresh job list
          if (onUploadSuccess) {
            onUploadSuccess();
          }
        }
      }
    });

    socket.on("resume_processed", (data) => {
      if (data.userId === user.id) {
        if (data.success) {
          setUploadStatus("success");
          setIsUploading(false);
          setProgress(100);
          // Call the success callback to refresh job list
          if (onUploadSuccess) {
            onUploadSuccess();
          }
        } else {
          setUploadStatus("error");
          setError(data.error || "Processing failed. Please try again.");
          setIsUploading(false);
        }
      }
    });

    socket.on("resume_error", (data) => {
      if (data.userId === user.id) {
        setUploadStatus("error");
        setError(data.error || "Processing failed. Please try again.");
        setIsUploading(false);
      }
    });

    socket.on("resume_processing", (data) => {
      if (data.userId === user.id) {
        setUploadStatus("processing");
        setProgress(data.progress || 50);
      }
    });

    return () => {
      socket.off("resume_progress");
      socket.off("resume_error");
      socket.off("resume_processing");
      socket.off("resume_processed");
    };
  }, [user?.id, onUploadSuccess]);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (
      selectedFile &&
      (selectedFile.type === "application/pdf" ||
        selectedFile.type === "application/msword" ||
        selectedFile.type ===
          "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    ) {
      setFile(selectedFile);
      setError("");
    } else {
      setFile(null);
      setError("Please select a valid PDF or Word document");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      setError("Please select a file to upload");
      return;
    }

    try {
      setIsUploading(true);
      setUploadStatus("uploading");
      setProgress(10);

      const formData = new FormData();
      formData.append("resume", file);
      formData.append("userId", user.id);

      const response = await fetch("http://localhost:5000/api/upload-resume", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to upload resume");
      }

      // Don't set progress to 30% here, let the WebSocket handle all progress updates
      setUploadStatus("processing");
      // Remove this line: setProgress(30);
      
    } catch (error) {
      console.error("Error uploading resume:", error);
      setError("Failed to upload resume. Please try again.");
      setUploadStatus("error");
      setIsUploading(false);
    }
  };

  // Rest of your component remains the same...
  return (
    <div className="flex justify-center items-center min-h-[60vh] bg-background">
      <Card className="w-full max-w-lg bg-card text-card-foreground border border-border rounded-lg shadow-lg">
        <CardHeader>
          <CardTitle className="text-center text-2xl font-bold">
            Upload Your Resume
          </CardTitle>
        </CardHeader>
        <CardContent>
          {uploadStatus === "success" ? (
            <div className="flex flex-col items-center space-y-2 text-center">
              <CheckCircle className="text-green-500 w-10 h-10" />
              <p className="font-semibold text-xl">Resume Uploaded Successfully!</p>
              <p className="text-muted-foreground text-lg">
                Your job recommendations are being prepared.
              </p>
            </div>
          ) : uploadStatus === "error" ? (
            <div className="flex flex-col items-center space-y-2 text-center">
              <AlertCircle className="text-red-500 w-10 h-10" />
              <p className="font-semibold text-xl">Upload Failed</p>
              <p className="text-destructive-foreground text-lg">{error}</p>
              <Button
                variant="outline"
                className="mt-4 text-lg"
                onClick={() => {
                  setUploadStatus(null);
                  setProgress(0);
                  setIsUploading(false);
                  setFile(null);
                  setError("");
                }}
              >
                Try Again
              </Button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6 text-center">
              <div className="flex flex-col items-center space-y-2">
                <Upload className="w-14 h-14 text-primary" />
                <p className="text-xl font-semibold">Select PDF or Word Document</p>
                <input
                  type="file"
                  accept=".pdf,.doc,.docx"
                  onChange={handleFileChange}
                  className="file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-lg file:font-semibold file:bg-primary file:text-primary-foreground hover:file:bg-primary/80"
                  disabled={isUploading}
                />
                {error && (
                  <span className="text-destructive text-lg">{error}</span>
                )}
              </div>
              {(isUploading || uploadStatus === "processing") && (
                <ProgressBar progress={progress} />
              )}
              <Button
                type="submit"
                className="w-full text-lg"
                disabled={isUploading}
              >
                {isUploading || uploadStatus === "processing"
                  ? uploadStatus === "uploading"
                    ? "Uploading your resume..."
                    : "Processing your resume..."
                  : "Upload Resume"}
              </Button>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// ProgressBar component
function ProgressBar({ progress }) {
  return (
    <div className="relative w-full h-6 bg-muted rounded-full overflow-hidden mt-2 mb-2">
      <div
        className="h-full bg-primary rounded-full transition-all duration-300"
        style={{ width: `${progress}%` }}
      ></div>
      <span className="absolute left-0 right-0 top-0 bottom-0 flex items-center justify-center text-white text-lg font-bold select-none">
        {progress < 100 ? `${progress}%` : "Complete"}
      </span>
    </div>
  );
}
