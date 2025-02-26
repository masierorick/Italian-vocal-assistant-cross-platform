import QtQuick 6.0
import QtQuick.Controls 6.0
import QtCore
import QtQml 2.15
import QtQml.Models 2.15
import QtQuick.Layouts 6.0

ApplicationWindow {
    id: window
    width: 600
    height: 300
    visible: true
    flags: Qt.FramelessWindowHint | Qt.Window
    color: "transparent"

    property string textColor: "white"
    property string nomebot: configData.botname

    Settings {
        id: settings
        property alias x: window.x
        property alias y: window.y
        property alias width: window.width
        property alias height: window.height
    }

    RowLayout {
        anchors.fill: parent
        spacing: 10

        // Sezione lista messaggi
        Rectangle {
            id: messageArea
            Layout.fillHeight: true
            Layout.fillWidth: true
            Layout.preferredWidth: window.width * 0.6
            color: "#80000000"
            radius: 10

            Flickable {
                id: flickable
                anchors.fill: parent
                contentHeight: testo.height
                clip: true

                Text {
                    objectName: "testo"
                    id: testo
                    text: ""
                    color: "white"
                    width: parent.width
                    wrapMode: Text.Wrap
                    font.pixelSize: 12
                    textFormat: Text.PlainText

                    onTextChanged: {
                        flickable.contentY = flickable.contentHeight - flickable.height
                    }
                }

                ScrollBar.vertical: ScrollBar {
                    policy: ScrollBar.AlwaysOn
                }
            }
        }

        // Sezione animazione e nome bot
        ColumnLayout {
            //Layout.fillHeight: true
            //Layout.preferredWidth: window.width * 0.4


            AnimatedImage {
                id: animation
                source: "breath_round.gif"
                width: 75
                height: 100
                smooth: false
                cache: true
            }

            Text {
                objectName: "botname"
                id: botname
                font.family: "Space Age"
                //x: (110/400)* parent.width
                width: animation.width/2
                height: animation.height
                font.bold: true
                font.pointSize: 50
                minimumPointSize: 5
                fontSizeMode: Text.Fit
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                color: textColor
                text: nomebot
            }
        }
    }

    MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.LeftButton | Qt.RightButton
        drag.target: parent
        onWheel: function(wheel) {
            let delta = wheel.angleDelta.y / 120;
            window.width += delta * 10;
            window.height += delta * 10;
            if (window.width < 200) window.width = 200;
            if (window.height < 100) window.height = 100;
        }
        onPressed: (mouse)=> {
            if (mouse.button == Qt.LeftButton)
                window.startSystemMove();
            else if (mouse.button == Qt.RightButton) {

                //processManager.stop_process();
                window.close();
            }
        }
    }

    // Connessione per aggiornare la lista dei comandi
    Connections {
        target: outputRedirector
        function onNewOutput(msg) {
            testo.text += msg + "\n";
        }
    }

    Timer {
        id: settingsCheckTimer
        interval: 1000
        running: true
        repeat: true
        onTriggered: {
                processManager.checkColor()
        }
    }
}
