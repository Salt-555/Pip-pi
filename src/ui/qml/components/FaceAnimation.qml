import QtQuick
import QtQuick.Controls

Rectangle {
    id: faceAnimation
    property string currentState: "WELCOME"
    property var frameIndex: 0
    property var currentFrames: []
    
    color: "transparent"
    border.width: 1
    border.color: themeController.buttonColor
    radius: themeController.cornerRadius

    Text {
        id: faceDisplay
        anchors.fill: parent
        anchors.margins: 10
        color: themeController.textColor
        font.family: "Courier New"
        font.pixelSize: calculateFontSize()
        text: currentFrames.length > 0 ? currentFrames[frameIndex] : ""
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        
        // Monitor size changes and update font size
        onWidthChanged: font.pixelSize = calculateFontSize()
        onHeightChanged: font.pixelSize = calculateFontSize()
    }

    Timer {
        id: animationTimer
        interval: 500 // 2 FPS default
        running: true
        repeat: true
        onTriggered: {
            if (currentFrames.length > 0) {
                frameIndex = (frameIndex + 1) % currentFrames.length;
                faceDisplay.text = currentFrames[frameIndex];
            }
        }
    }

    function setState(state) {
        currentState = state;
        frameIndex = 0;
        currentFrames = FaceController.getFramesForState(state);
        faceDisplay.font.pixelSize = calculateFontSize();
    }

    function calculateFontSize() {
        if (!currentFrames.length) return 16;
        
        let frame = currentFrames[0];
        let lines = frame.split('\n');
        let maxWidth = Math.max(...lines.map(line => line.length));
        let numLines = lines.length;
        
        // Calculate available space (accounting for margins)
        let availableWidth = width - 20;  // 10px margin on each side
        let availableHeight = height - 20; // 10px margin on each side
        
        // Calculate size based on width and height constraints
        let widthBasedSize = (availableWidth * 0.8) / (maxWidth * 0.6);
        let heightBasedSize = (availableHeight * 0.8) / (numLines * 1.2);
        
        // Use the smaller of the two sizes to ensure text fits both dimensions
        let fontSize = Math.min(widthBasedSize, heightBasedSize);
        
        // Ensure minimum and maximum reasonable sizes
        return Math.max(Math.min(fontSize, 48), 8);
    }

    Component.onCompleted: {
        setState("WELCOME");
        // Switch to IDLE after 5 seconds
        switchToIdleTimer.start();
    }

    Timer {
        id: switchToIdleTimer
        interval: 5000
        repeat: false
        onTriggered: {
            setState("IDLE");
        }
    }
}