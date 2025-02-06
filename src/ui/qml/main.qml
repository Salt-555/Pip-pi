import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 1000
    height: 800
    title: "Pip-Pi Assistant (QML)"
    
    // Center on screen
    Component.onCompleted: {
        x = (Screen.width - width) / 2
        y = (Screen.height - height) / 2
    }
    
    // Main content will go here
    ColumnLayout {
        anchors.fill: parent
        spacing: 10
        
        // Placeholder text to verify it's working
        Label {
            Layout.alignment: Qt.AlignCenter
            text: "QML Version - Coming Soon"
            font.pixelSize: 24
        }
    }
}