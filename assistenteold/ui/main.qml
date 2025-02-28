import QtQuick 6.0
import QtQuick.Controls 6.0
import QtCore



ApplicationWindow  {
    id: window
    width: settings.width
    height: settings.height
    visible: true
    flags: Qt.FramelessWindowHint | Qt.Window
    color: "transparent"
    property string textColor: "white"
    property string nomebot: configData.botname

    Settings {
        id: settings

        property alias x : window.x
        property alias y : window.y
        property alias width : window.width
        property alias height : window.height
        onWidthChanged: {
            settings.width = window.width;
        }
        onHeightChanged: {
            settings.height = window.height;
        }
    }



    Timer {
        id: settingsCheckTimer
        interval: 1000 // intervallo in millisecondi (1 secondo)
        running: true
        repeat: true
        onTriggered: {
            // Avvio processo di controllo se il botname è attivo e relativo cambio di colore
            processManager.checkColor()
        }
    }

    AnimatedImage {
        id: animation
        anchors.fill: parent
        source: "breath_round.gif"
        height: 100; width: 75
        //fillMode: Image.PreserveAspectFit
        smooth: false
        cache: true

    }

    Text {
            objectName: "botname"
            id:botname
            x: (110/400)* parent.width
            width: parent.width/2
            height: parent.height
            font.family: "Space Age"
            anchors.fill: parent
            font.bold: true
            font.pointSize: 50
            minimumPointSize: 5
            fontSizeMode: Text.Fit
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            color: textColor
            text: nomebot


     }



    MouseArea {
      anchors.fill: parent
      acceptedButtons: Qt.LeftButton | Qt.RightButton
      drag.target: parent
      onWheel: function(wheel) {
                let delta = wheel.angleDelta.y / 120; // 120 è il valore tipico per una rotazione del mouse wheel
                window.width += delta * 10; // Cambia la larghezza
                window.height += delta * 10; // Cambia l'altezza


                // Assicuriamoci che la finestra non diventi troppo piccola
                if (window.width < 100) window.width = 100;
                if (window.height < 75) window.height = 75;
            }
      onPressed: (mouse)=> {
            if (mouse.button == Qt.LeftButton)
                window.startSystemMove();
            else
             if (mouse.button == Qt.RightButton) {
                processManager.stop_process()
                window.close();
           }
        }
     }


     Component.onCompleted: {

         }


    Component.onDestruction: {

    }

}

