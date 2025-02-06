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
    title: "Pip-Pi Assistant (QML)"
    color: themeController.backgroundColor

    // Center on screen on startup
    Component.onCompleted: {
        x = Screen.width / 2 - width / 2
        y = Screen.height / 2 - height / 2
    }

    // Main content layout
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        // Top bar with personality selector
        ComboBox {
            id: personalitySelector
            model: ["Conversational", "Analytical"]
            implicitWidth: 200
            currentIndex: model.indexOf(settingsController.personality.charAt(0).toUpperCase() + 
                                      settingsController.personality.slice(1))

            background: Rectangle {
                color: themeController.buttonColor
                radius: themeController.cornerRadius
                border.width: 1
                border.color: themeController.accentColor
            }

            contentItem: Text {
                text: personalitySelector.displayText
                color: themeController.textColor
                font.family: themeController.fontFamily
                font.pixelSize: themeController.fontSize
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignLeft
                leftPadding: 10
            }

            popup: Popup {
                y: personalitySelector.height
                width: personalitySelector.width
                padding: 1

                background: Rectangle {
                    color: themeController.backgroundColor
                    border.color: themeController.accentColor
                    radius: themeController.cornerRadius
                }

                contentItem: ListView {
                    clip: true
                    implicitHeight: contentHeight
                    model: personalitySelector.popup.visible ? personalitySelector.delegateModel : null
                    ScrollIndicator.vertical: ScrollIndicator {}
                }
            }

            delegate: ItemDelegate {
                width: personalitySelector.width
                height: 40

                background: Rectangle {
                    color: highlighted ? themeController.buttonActiveColor : "transparent"
                }

                contentItem: Text {
                    text: modelData
                    color: themeController.textColor
                    font.family: themeController.fontFamily
                    font.pixelSize: themeController.fontSize
                    verticalAlignment: Text.AlignVCenter
                    leftPadding: 10
                }

                highlighted: personalitySelector.highlightedIndex === index
            }

            onActivated: settingsController.personality = currentText.toLowerCase()
        }

        // Middle section with chat and face
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 10

            // Chat area (left side)
            ScrollView {
                id: chatScrollView
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredWidth: parent.width * 0.7
                clip: true

                background: Rectangle {
                    color: themeController.backgroundColor
                    radius: themeController.cornerRadius
                    border.width: 1
                    border.color: themeController.buttonColor
                }

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

            // Face and monitor area (right side)
            ColumnLayout {
                Layout.fillHeight: true
                Layout.preferredWidth: parent.width * 0.3
                spacing: 10

                // Face animation area
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 300
                    color: "transparent"
                    border.width: 1
                    border.color: themeController.buttonColor
                    radius: themeController.cornerRadius

                    Text {
                        anchors.centerIn: parent
                        text: "[Face Animation]"
                        color: themeController.textColor
                        font.family: themeController.fontFamily
                        font.pixelSize: themeController.fontSize
                    }
                }

                // System monitor area
                Rectangle {
                    id: monitorArea
                    Layout.fillWidth: true
                    Layout.preferredHeight: 120
                    color: "transparent"
                    border.width: 1
                    border.color: themeController.buttonColor
                    radius: themeController.cornerRadius
                    visible: true

                    Text {
                        anchors.centerIn: parent
                        text: "[System Monitor]"
                        color: themeController.textColor
                        font.family: themeController.fontFamily
                        font.pixelSize: themeController.fontSize
                    }
                }

                Item {
                    Layout.fillHeight: true
                }
            }
        }

        // Bottom input area
        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            ScrollView {
                Layout.fillWidth: true
                Layout.preferredHeight: inputField.implicitHeight
                clip: true

                background: Rectangle {
                    color: themeController.inputBgColor
                    radius: themeController.cornerRadius
                    border.width: 1
                    border.color: themeController.buttonColor
                }

                TextArea {
                    id: inputField
                    placeholderText: "Type your message here..."
                    placeholderTextColor: Qt.darker(themeController.textColor, 1.5)
                    wrapMode: TextArea.Wrap
                    color: themeController.textColor
                    font.family: themeController.fontFamily
                    font.pixelSize: themeController.fontSize
                    padding: 10

                    background: Rectangle {
                        color: "transparent"
                    }

                    Keys.onReturnPressed: {
                        if (!(event.modifiers & Qt.ShiftModifier)) {
                            // Send message handling will go here
                            event.accepted = true
                        }
                    }
                }
            }

            Button {
                id: sendButton
                text: "Send"
                implicitWidth: 100
                implicitHeight: 40

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
            }

            Button {
                id: settingsButton
                text: "Settings"
                implicitWidth: 100
                implicitHeight: 40

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

    // Settings popup component
    SettingsPopup {
        id: settingsPopup
    }
}