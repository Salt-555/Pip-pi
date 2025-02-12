// FaceAnimation.qml
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

    // Container for the face display with clipping
    Item {
        id: displayContainer
        anchors.fill: parent
        anchors.margins: 10
        clip: true

        Text {
            id: faceDisplay
            anchors.centerIn: parent
            color: themeController.textColor
            font.family: "Courier New"
            font.pixelSize: calculateFontSize()
            text: currentFrames.length > 0 ? currentFrames[frameIndex] : ""
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }
    }

    Timer {
        id: animationTimer
        interval: 500 // 2 FPS default
        running: true
        repeat: true
        onTriggered: {
            if (currentFrames.length > 0) {
                frameIndex = (frameIndex + 1) % currentFrames.length;
            }
        }
    }

    function setState(state) {
        currentState = state;
        frameIndex = 0;
        currentFrames = faceController.getFramesForState(state);
    }

    function calculateFontSize() {
        if (!currentFrames.length) return 16;
        
        let frame = currentFrames[frameIndex];
        let lines = frame.split('\n');
        let maxWidth = Math.max(...lines.map(line => line.length));
        let numLines = lines.length;
        
        // Get container dimensions minus padding
        let availableWidth = displayContainer.width - 20;  // 10px padding each side
        let availableHeight = displayContainer.height - 20; // 10px padding each side
        
        // Calculate font size based on both width and height constraints
        let widthBasedSize = availableWidth / (maxWidth * 0.6);  // character width ratio
        let heightBasedSize = availableHeight / (numLines * 1.2); // line height ratio
        
        // Use the more constraining size
        let calculatedSize = Math.min(widthBasedSize, heightBasedSize);
        
        // Clamp between minimum of 2px and maximum of 24px
        return Math.max(Math.min(calculatedSize, 24), 2);
    }

    Component.onCompleted: {
        setState("WELCOME");
    }
}