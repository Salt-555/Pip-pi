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
    minimumHeight: 600
    title: "Pip-Pi Assistant (QML)"
    color: themeController.backgroundColor

    // Center on screen on startup
    Component.onCompleted: {
        x = Screen.width / 2 - width / 2
        y = Screen.height / 2 - height / 2
    }

    // Main layout container
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

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

                ScrollView {
                    id: chatScrollView
                    anchors.fill: parent
                    anchors.margins: 1
                    clip: true

                    TextArea {
                        id: chatArea
                        readOnly: true
                        wrapMode: TextArea.Wrap
                        selectByMouse: true
                        selectByKeyboard: true
                        color: themeController.textColor
                        font.family: themeController.fontFamily
                        font.pixelSize: themeController.fontSize
                        padding: 10

                        background: Rectangle {
                            color: "transparent"
                        }
                    }
                }
            }

            // Face area
            ColumnLayout {
                Layout.fillHeight: true
                Layout.minimumWidth: 200
                Layout.preferredWidth: parent.width * 0.3
                Layout.maximumWidth: parent.width * 0.4
                spacing: 10

                FaceAnimation {
                    Layout.fillWidth: true
                    Layout.minimumHeight: 250
                    Layout.preferredHeight: 300
                    Layout.maximumHeight: 400
                }

                Item {
                    Layout.fillHeight: true
                    Layout.fillWidth: true
                }
            }
        }

        // Input area
        RowLayout {
            Layout.fillWidth: true
            Layout.preferredHeight: Math.min(Math.max(35, inputField.contentHeight + 16), 75)
            Layout.maximumHeight: 75
            Layout.bottomMargin: 10
            spacing: 10

            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: themeController.inputBgColor
                radius: themeController.cornerRadius
                border.width: 1
                border.color: themeController.buttonColor

                ScrollView {
                    anchors.fill: parent
                    anchors.margins: 1
                    clip: true

                    TextArea {
                        id: inputField
                        height: parent.height
                        placeholderText: "Type your message here..."
                        placeholderTextColor: Qt.darker(themeController.textColor, 1.5)
                        wrapMode: TextArea.Wrap
                        color: themeController.textColor
                        font.family: themeController.fontFamily
                        font.pixelSize: themeController.fontSize
                        topPadding: 8
                        bottomPadding: 8
                        leftPadding: 10
                        rightPadding: 10

                        background: Rectangle {
                            color: "transparent"
                        }

                        Keys.onReturnPressed: {
                            if (!(event.modifiers & Qt.ShiftModifier)) {
                                if (text.trim().length > 0) {
                                    // TODO: Implement message sending
                                }
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

                Button {
                    id: sendButton
                    Layout.preferredWidth: 100
                    Layout.preferredHeight: 35
                    text: "Send"

                    background: Rectangle {
                        color: parent.pressed ? themeController.buttonActiveColor : themeController.buttonColor
                        radius: themeController.cornerRadius
                        border.width: 1
                        border.color: themeController.accentColor

                        Behavior on color {
                            ColorAnimation { duration: 50 }
                        }
                    }

                    contentItem: Text {
                        text: sendButton.text
                        color: themeController.textColor
                        font.family: themeController.fontFamily
                        font.pixelSize: themeController.fontSize
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    onClicked: {
                        if (inputField.text.trim().length > 0) {
                            // TODO: Implement message sending
                        }
                    }
                }

                Button {
                    id: settingsButton
                    Layout.preferredWidth: 100
                    Layout.preferredHeight: 35
                    text: "Settings"

                    background: Rectangle {
                        color: parent.pressed ? themeController.buttonActiveColor : themeController.buttonColor
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

    // Settings popup
    SettingsPopup {
        id: settingsPopup
    }
}