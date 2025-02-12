import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window
import "components"

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 1000
    height: 800
    minimumWidth: 800
    minimumHeight: 500
    title: "Pip-Pi Assistant"
    color: themeController.backgroundColor

    // Center on screen on startup
    Component.onCompleted: {
        x = Screen.width / 2 - width / 2
        y = Screen.height / 2 - height / 2
    }

    // Custom message delegate for chat
    Component {
        id: messageDelegate
        Column {
            width: ListView.view.width
            spacing: 4
            topPadding: 4
            bottomPadding: 4

            Rectangle {
                width: messageContent.width + 24
                height: messageContent.height + 16
                color: {
                    switch(model.type) {
                        case "user": return Qt.alpha(themeController.accentColor, 0.1)
                        case "ai": return Qt.alpha(themeController.aiColor, 0.1)
                        case "error": return Qt.alpha("#FF0000", 0.1)
                        default: return "transparent"
                    }
                }
                radius: 8
                anchors.right: model.type === "user" ? parent.right : undefined
                anchors.left: model.type !== "user" ? parent.left : undefined

                Text {
                    id: messageContent
                    text: model.text
                    color: {
                        switch(model.type) {
                            case "user": return themeController.accentColor
                            case "ai": return themeController.aiColor
                            case "error": return "#FF0000"
                            default: return themeController.textColor
                        }
                    }
                    font.family: themeController.fontFamily
                    font.pixelSize: themeController.fontSize
                    wrapMode: Text.WordWrap
                    width: Math.min(parent.parent.width * 0.9, implicitWidth)
                    anchors.centerIn: parent
                }
            }
        }
    }

    // Main layout
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        // Title display area
        TitleDisplay {
            id: titleDisplay
            Layout.fillWidth: true
            Layout.preferredHeight: 60
            currentText: settingsController.personality.toUpperCase()

            Connections {
                target: settingsController
                function onPersonalityChanged() {
                    titleDisplay.updateText(settingsController.personality.toUpperCase())
                }
            }
        }

        // Main content area
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 10

            // Chat area
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredWidth: parent.width * 0.7
                Layout.minimumWidth: 400
                color: "transparent"
                border.width: 1
                border.color: themeController.buttonColor
                radius: themeController.cornerRadius

                ListView {
                    id: chatView
                    anchors.fill: parent
                    anchors.margins: 10
                    clip: true
                    model: ListModel { 
                        id: chatModel 
                        property int messageCounter: 0
                    }
                    delegate: messageDelegate
                    spacing: 8
                    
                    ScrollBar.vertical: ScrollBar {
                        active: chatView.moving || chatView.pressed
                    }
                    
                    // Auto-scroll to bottom
                    onCountChanged: positionViewAtEnd()
                }
            }

            // Right side panel
            ColumnLayout {
                Layout.fillHeight: true
                Layout.minimumWidth: 200
                Layout.preferredWidth: parent.width * 0.3
                Layout.maximumWidth: parent.width * 0.4
                spacing: 10

                // Face animation
                FaceAnimation {
                    id: faceAnimation
                    Layout.fillWidth: true
                    Layout.minimumHeight: 250
                    Layout.preferredHeight: 300
                    Layout.maximumHeight: 400

                    Connections {
                        target: settingsController
                        function onPersonalityChanged() {
                            if (settingsController.personality === "analytical") {
                                faceAnimation.setState("ANALYSIS")
                            } else if (settingsController.personality === "conversational") {
                                faceAnimation.setState("CHATTING")
                            }
                        }
                    }

                    Timer {
                        id: stateResetTimer
                        interval: 4000
                        repeat: false
                        onTriggered: faceAnimation.setState("IDLE")
                    }

                    // Watch for state changes and restart timer when needed
                    onCurrentStateChanged: {
                        if (currentState === "ANALYSIS" || currentState === "CHATTING") {
                            stateResetTimer.restart()
                        }
                    }
                }

                // Spacer
                Item {
                    Layout.fillHeight: true
                }
            }
        }

        // Input area
        RowLayout {
            Layout.fillWidth: true
            Layout.preferredHeight: Math.min(Math.max(35, inputField.contentHeight + 16), 75)
            Layout.maximumHeight: 75
            spacing: 10

            // Text input
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: themeController.inputBgColor
                radius: themeController.cornerRadius
                border.width: 1
                border.color: chatController.isThinking ? 
                    themeController.aiColor : themeController.buttonColor

                ScrollView {
                    anchors.fill: parent
                    anchors.margins: 1
                    clip: true

                    TextArea {
                        id: inputField
                        placeholderText: chatController.isThinking ? 
                            "Thinking..." : "Type your message here..."
                        placeholderTextColor: Qt.darker(themeController.textColor, 1.5)
                        wrapMode: TextArea.Wrap
                        color: themeController.textColor
                        font.family: themeController.fontFamily
                        font.pixelSize: themeController.fontSize
                        enabled: !chatController.isThinking
                        topPadding: 8
                        bottomPadding: 8
                        leftPadding: 10
                        rightPadding: 10

                        background: Rectangle {
                            color: "transparent"
                        }

                        Keys.onReturnPressed: function(event) {
                            if (!(event.modifiers & Qt.ShiftModifier)) {
                                sendMessage()
                                event.accepted = true
                            }
                        }
                    }
                }
            }

            // Buttons
            RowLayout {
                Layout.preferredWidth: 220
                Layout.preferredHeight: 35
                spacing: 10

                // Send button
                Button {
                    id: sendButton
                    Layout.preferredWidth: 100
                    Layout.preferredHeight: 35
                    text: "Send"
                    enabled: !chatController.isThinking && inputField.text.trim().length > 0

                    background: Rectangle {
                        color: parent.pressed ? themeController.buttonActiveColor : 
                               parent.enabled ? themeController.buttonColor : 
                               Qt.darker(themeController.buttonColor, 1.5)
                        radius: themeController.cornerRadius
                        border.width: 1
                        border.color: themeController.accentColor

                        Behavior on color {
                            ColorAnimation { duration: 50 }
                        }
                    }

                    contentItem: Text {
                        text: sendButton.text
                        color: sendButton.enabled ? themeController.textColor : 
                               Qt.darker(themeController.textColor, 1.5)
                        font.family: themeController.fontFamily
                        font.pixelSize: themeController.fontSize
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    onClicked: sendMessage()
                }

                // Settings button
                Button {
                    id: settingsButton
                    Layout.preferredWidth: 100
                    Layout.preferredHeight: 35
                    text: "Settings"

                    background: Rectangle {
                        color: parent.pressed ? themeController.buttonActiveColor : 
                               themeController.buttonColor
                        radius: themeController.cornerRadius
                        border.width: 1
                        border.color: themeController.accentColor

                        Behavior on color {
                            ColorAnimation { duration: 50 }
                        }
                    }

                    contentItem: Text {
                        text: settingsButton.text
                        color: themeController.textColor
                        font.family: themeController.fontFamily
                        font.pixelSize: themeController.fontSize
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    onClicked: settingsPopup.open()
                }
            }
        }
    }

    // Function to handle message sending
    function sendMessage() {
        let text = inputField.text.trim()
        if (text.length > 0 && !chatController.isThinking) {
            chatController.sendMessage(text)
            inputField.text = ""
        }
    }

    // Chat controller connections
    Connections {
        target: chatController
        
        function onMessageReceived(message, type) {
            chatModel.messageCounter++
            chatModel.append({
                "messageId": chatModel.messageCounter,
                "text": message, 
                "type": type
            })
        }
        
        function onMessageUpdated(messageId, newText) {
            // Find and update the message with the matching ID
            for(let i = 0; i < chatModel.count; i++) {
                if(chatModel.get(i).messageId === messageId) {
                    chatModel.setProperty(i, "text", newText)
                    break
                }
            }
        }
        
        function onThinkingStateChanged(thinking) {
            if (thinking) {
                faceAnimation.setState("THINKING")
            } else {
                faceAnimation.setState("IDLE")
            }
        }
        
        function onErrorOccurred(error) {
            chatModel.messageCounter++
            chatModel.append({
                "messageId": chatModel.messageCounter,
                "text": error,
                "type": "error"
            })
        }
    }

    // Settings popup
    SettingsPopup {
        id: settingsPopup
    }
}