import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Popup {
    id: settingsPopup
    width: 400
    height: contentHeight
    padding: 2

    // Position above the settings button
    y: parent.height - height - settingsButton.height - 10
    x: parent.width - width - 10

    // Close when clicking outside
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

    background: Rectangle {
        color: themeController.backgroundColor
        border.color: themeController.accentColor
        border.width: 2
        radius: themeController.cornerRadius
    }

    contentItem: ColumnLayout {
        spacing: 20
        width: parent.width

        // Header
        Label {
            text: "Settings"
            color: themeController.textColor
            font {
                family: themeController.fontFamily
                pixelSize: themeController.fontSize + 4
                bold: true
            }
            Layout.alignment: Qt.AlignHCenter
            Layout.topMargin: 10
        }

        // Theme Selection
        ColumnLayout {
            spacing: 5
            Layout.fillWidth: true
            Layout.margins: 10

            Label {
                text: "Theme"
                color: themeController.textColor
                font.family: themeController.fontFamily
                font.pixelSize: themeController.fontSize
            }

            ComboBox {
                id: themeCombo
                model: themeController.getAvailableThemes()
                Layout.fillWidth: true
                
                Component.onCompleted: {
                    currentIndex = model.indexOf(themeController.currentTheme)
                }

                background: Rectangle {
                    color: themeController.buttonColor
                    radius: themeController.cornerRadius
                    border.width: 1
                    border.color: themeController.accentColor
                }

                contentItem: Text {
                    text: themeCombo.displayText
                    color: themeController.textColor
                    font.family: themeController.fontFamily
                    font.pixelSize: themeController.fontSize
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignLeft
                    leftPadding: 10
                }

                popup: Popup {
                    y: themeCombo.height
                    width: themeCombo.width
                    padding: 1

                    background: Rectangle {
                        color: themeController.backgroundColor
                        border.color: themeController.accentColor
                        radius: themeController.cornerRadius
                    }

                    contentItem: ListView {
                        clip: true
                        implicitHeight: contentHeight
                        model: themeCombo.popup.visible ? themeCombo.delegateModel : null
                        ScrollIndicator.vertical: ScrollIndicator {}
                    }
                }

                delegate: ItemDelegate {
                    width: themeCombo.width
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

                    highlighted: themeCombo.highlightedIndex === index
                }

                onActivated: themeController.setTheme(currentText)
            }
        }

        // Personality Selection
        ColumnLayout {
            spacing: 5
            Layout.fillWidth: true
            Layout.margins: 10

            Label {
                text: "Personality"
                color: themeController.textColor
                font.family: themeController.fontFamily
                font.pixelSize: themeController.fontSize
            }

            ComboBox {
                id: personalityCombo
                model: ["Conversational", "Analytical"]
                Layout.fillWidth: true
                
                Component.onCompleted: {
                    currentIndex = model.indexOf(settingsController.personality.charAt(0).toUpperCase() + 
                                              settingsController.personality.slice(1))
                }

                background: Rectangle {
                    color: themeController.buttonColor
                    radius: themeController.cornerRadius
                    border.width: 1
                    border.color: themeController.accentColor
                }

                contentItem: Text {
                    text: personalityCombo.displayText
                    color: themeController.textColor
                    font.family: themeController.fontFamily
                    font.pixelSize: themeController.fontSize
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignLeft
                    leftPadding: 10
                }

                popup: Popup {
                    y: personalityCombo.height
                    width: personalityCombo.width
                    padding: 1

                    background: Rectangle {
                        color: themeController.backgroundColor
                        border.color: themeController.accentColor
                        radius: themeController.cornerRadius
                    }

                    contentItem: ListView {
                        clip: true
                        implicitHeight: contentHeight
                        model: personalityCombo.popup.visible ? personalityCombo.delegateModel : null
                        ScrollIndicator.vertical: ScrollIndicator {}
                    }
                }

                delegate: ItemDelegate {
                    width: personalityCombo.width
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

                    highlighted: personalityCombo.highlightedIndex === index
                }

                onActivated: settingsController.personality = currentText.toLowerCase()
            }
        }

        // Volume Control
        ColumnLayout {
            spacing: 5
            Layout.fillWidth: true
            Layout.margins: 10

            Label {
                text: "Volume"
                color: themeController.textColor
                font.family: themeController.fontFamily
                font.pixelSize: themeController.fontSize
            }

            Item {
                Layout.fillWidth: true
                height: 32

                // Background track
                Rectangle {
                    anchors.verticalCenter: parent.verticalCenter
                    width: parent.width
                    height: 4
                    radius: 2
                    color: themeController.buttonColor

                    // Progress track
                    Rectangle {
                        width: volumeSlider.visualPosition * parent.width
                        height: parent.height
                        color: themeController.accentColor
                        radius: 2
                    }
                }

                // The actual interactive slider
                Slider {
                    id: volumeSlider
                    anchors.fill: parent
                    from: 0
                    to: 100
                    stepSize: 1
                    value: settingsController.volume
                    live: true
                    background: Item {} // Empty background since we draw it separately
                    handle: Rectangle {
                        x: volumeSlider.visualPosition * (volumeSlider.width - width)
                        y: (volumeSlider.height - height) / 2
                        width: 16
                        height: 16
                        radius: 8
                        color: volumeSlider.pressed ? themeController.buttonActiveColor : themeController.buttonColor
                        border.color: themeController.accentColor
                        z: 2  // Ensure handle is on top
                    }

                    onValueChanged: {
                        if (pressed) {
                            settingsController.volume = value
                        }
                    }
                }
            }

            Label {
                text: Math.round(volumeSlider.value) + "%"
                color: themeController.textColor
                font.family: themeController.fontFamily
                font.pixelSize: themeController.fontSize
                Layout.preferredWidth: 50
            }
        }

        // Bottom padding
        Item {
            height: 10
        }
    }
}