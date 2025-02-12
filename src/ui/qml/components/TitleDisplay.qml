// TitleDisplay.qml
import QtQuick
import QtQuick.Controls

Rectangle {
    id: root
    color: "transparent"
    border.width: 1
    border.color: themeController.buttonColor
    radius: themeController.cornerRadius

    property string currentText: ""
    property bool animating: false

    // Container for the current text
    Text {
        id: displayText
        anchors.centerIn: parent
        text: root.currentText
        color: themeController.textColor
        font.family: "Courier New"
        font.pixelSize: 24
        font.bold: true
        opacity: root.animating ? 0 : 1

        Behavior on opacity {
            NumberAnimation { duration: 150 }
        }
    }

    // Text that appears during transition
    Text {
        id: transitionText
        anchors.centerIn: parent
        color: themeController.textColor
        font.family: "Courier New"
        font.pixelSize: 24
        font.bold: true
        opacity: root.animating ? 1 : 0

        Behavior on opacity {
            NumberAnimation { duration: 150 }
        }
    }

    // Function to trigger text change with animation
    function updateText(newText) {
        if (!root.animating) {
            root.animating = true;
            
            // Start noise effect
            noiseTimer.start();
            
            // Schedule the actual text change
            textChangeTimer.interval = 300;  // Show noise for 300ms
            textChangeTimer.triggered.connect(function() {
                root.currentText = newText;
                root.animating = false;
                noiseTimer.stop();
            });
            textChangeTimer.start();
        }
    }

    // Timer for actual text change
    Timer {
        id: textChangeTimer
        repeat: false
    }

    // Timer for generating "noise" during transitions
    Timer {
        id: noiseTimer
        interval: 50
        repeat: true
        running: false
        onTriggered: {
            let chars = "▀▄█▌▐░▒▓";
            let noiseString = "";
            let length = Math.max(currentText.length, 20); // Minimum length for short text
            
            for (let i = 0; i < length; i++) {
                noiseString += chars[Math.floor(Math.random() * chars.length)];
            }
            
            transitionText.text = noiseString;
        }
    }
}