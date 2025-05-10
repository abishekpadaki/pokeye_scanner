document.addEventListener('DOMContentLoaded', () => {
    const cameraFeed = document.getElementById('cameraFeed');
    const photoCanvas = document.getElementById('photoCanvas');
    const captureBtn = document.getElementById('captureBtn');
    const flipCameraBtn = document.getElementById('flipCameraBtn');
    const jsonOutput = document.getElementById('jsonOutput');

    let currentStream;
    let facingMode = 'environment'; // Prefer back camera
    let availableVideoInputs = [];
    let currentVideoInputIndex = 0;

    const backendUrl = '/api/scan-card'; // Placeholder, will be Flask endpoint

    async function getConnectedDevices(type) {
        const devices = await navigator.mediaDevices.enumerateDevices();
        return devices.filter(device => device.kind === type);
    }

    async function startCamera(videoDeviceId = undefined) {
        if (currentStream) {
            currentStream.getTracks().forEach(track => track.stop());
        }

        let constraints = {
            video: {
                facingMode: facingMode
            },
            audio: false
        };

        if (videoDeviceId) {
            constraints.video.deviceId = { exact: videoDeviceId };
        } else {
            // Fallback if specific deviceId fails or not provided
            constraints.video.facingMode = facingMode;
        }
        
        try {
            currentStream = await navigator.mediaDevices.getUserMedia(constraints);
            cameraFeed.srcObject = currentStream;
            await cameraFeed.play(); // Ensure video plays

            // Update available video inputs for flipping
            const videoInputs = await getConnectedDevices('videoinput');
            availableVideoInputs = videoInputs;
            if (videoInputs.length > 1) {
                flipCameraBtn.style.display = 'inline-block';
                // Try to find current device in the list to set index
                const currentDevice = currentStream.getVideoTracks()[0].getSettings().deviceId;
                currentVideoInputIndex = availableVideoInputs.findIndex(device => device.deviceId === currentDevice);
            } else {
                flipCameraBtn.style.display = 'none';
            }

        } catch (err) {
            console.error("Error accessing camera: ", err);
            jsonOutput.textContent = `Error accessing camera: ${err.name}. Please ensure permissions are granted and you are using HTTPS if not on localhost.`;
            if (err.name === "OverconstrainedError" && !videoDeviceId) {
                // If default facingMode failed, try the other one
                console.log("Trying alternate facing mode.");
                facingMode = (facingMode === 'user') ? 'environment' : 'user';
                startCamera(); // Retry with alternate mode
            }
        }
    }

    flipCameraBtn.addEventListener('click', () => {
        if (availableVideoInputs.length > 1) {
            currentVideoInputIndex = (currentVideoInputIndex + 1) % availableVideoInputs.length;
            const nextVideoDeviceId = availableVideoInputs[currentVideoInputIndex].deviceId;
            // If we successfully got a deviceId, update facingMode based on its label
            // This is a heuristic as actual facingMode isn't always directly available post-selection this way
            const deviceLabel = availableVideoInputs[currentVideoInputIndex].label.toLowerCase();
            if (deviceLabel.includes('front') || deviceLabel.includes('user')) {
                facingMode = 'user';
            } else if (deviceLabel.includes('back') || deviceLabel.includes('environment')) {
                facingMode = 'environment';
            }
            startCamera(nextVideoDeviceId);
        }
    });

    captureBtn.addEventListener('click', async () => {
        if (!currentStream) {
            jsonOutput.textContent = 'Camera not active. Please start the camera first.';
            return;
        }

        jsonOutput.textContent = 'Processing...';
        const context = photoCanvas.getContext('2d');
        
        // Set canvas dimensions to video stream dimensions
        const videoTrack = currentStream.getVideoTracks()[0];
        const settings = videoTrack.getSettings();
        photoCanvas.width = settings.width || cameraFeed.videoWidth;
        photoCanvas.height = settings.height || cameraFeed.videoHeight;

        // Flip context if video is mirrored (e.g., front camera)
        // The video feed CSS already mirrors it, so we draw it normally and the CSS handles the visual.
        // However, if the actual image data needs to be unmirrored, do it here.
        // For now, assume the backend can handle potentially mirrored images or the CSS mirror is sufficient for user alignment.
        // if (facingMode === 'user') {
        //     context.translate(photoCanvas.width, 0);
        //     context.scale(-1, 1);
        // }

        context.drawImage(cameraFeed, 0, 0, photoCanvas.width, photoCanvas.height);
        
        // Get image data from canvas
        // Use 'image/jpeg' for smaller file size, 'image/png' for better quality
        const imageDataUrl = photoCanvas.toDataURL('image/jpeg', 0.9); 

        try {
            const response = await fetch(backendUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ image: imageDataUrl }),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Unknown error from server' }));
                throw new Error(`Server error: ${response.status} ${response.statusText}. ${errorData.detail}`);
            }

            const data = await response.json();
            jsonOutput.textContent = JSON.stringify(data, null, 2);

        } catch (err) {
            console.error('Error sending image to backend:', err);
            jsonOutput.textContent = `Error: ${err.message}`;
        }
    });

    // Initialize camera on load
    startCamera();
}); 