import QtQuick 6.0
import QtQuick.Controls 6.0
import Qt.labs.settings 1.1

Window {
    id:appWindow
    visible: true
    flags: Qt.FramelessWindowHint | Qt.Window
    color: "transparent"

    Settings {
        id: windowSettings
        property  int savedX: 200
        property  int savedY: 200
        property int savedWidth : 400
        property int savedHeight : 200
    }

    x: windowSettings.savedX
    y: windowSettings.savedY
    width: 0 //windowSettings.savedWidth
    height: 0 //windowSettings.savedHeight

    // Animazione per la larghezza
        Behavior on width {
            NumberAnimation {
                duration: 500  // Durata in millisecondi
                easing.type: Easing.InOutQuad  // Tipo di easing
            }
        }

        // Animazione per l'altezza
        Behavior on height {
            NumberAnimation {
                duration: 500  // Durata in millisecondi
                easing.type: Easing.InOutQuad  // Tipo di easing
            }
        }

        // Animazione all'apertura della pagina
        Component.onCompleted: {
            width = windowSettings.savedWidth
            height = windowSettings.savedHeight
        }

    // Monitoraggio dei cambiamenti di posizione per salvarli
    onXChanged: windowSettings.savedX = x
    onYChanged: windowSettings.savedY = y

    Rectangle {
        id: rectangle
        color: "#80000000"  // Semitrasparente
        radius: 10
        anchors.fill: parent
        anchors.margins: 10


        Flickable {
            id: flickable
            anchors.fill: parent
            anchors.margins: 10
            contentWidth: testo.width
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
                   flickable.contentY = flickable.contentHeight - flickable.height;
                }
            }
           ScrollBar.vertical: ScrollBar {
            policy: ScrollBar.AlwaysOn
           }
        }


         MouseArea {
            id: mouseArea
            anchors.fill: parent
            acceptedButtons: Qt.LeftButton | Qt.RightButton
            hoverEnabled: true

            property int edgeMargin: 10

             function updateCursorShape(mouseX, mouseY) {
               if (mouseX < edgeMargin && mouseY < edgeMargin)
                mouseArea.cursorShape = Qt.SizeFDiagCursor;  // Angolo in alto a sinistra
               else if (mouseX > width - edgeMargin && mouseY > height - edgeMargin)
                mouseArea.cursorShape = Qt.SizeFDiagCursor;  // Angolo in basso a destra
               else if (mouseX < edgeMargin && mouseY > height - edgeMargin)
                mouseArea.cursorShape = Qt.SizeBDiagCursor;  // Angolo in basso a sinistra
               else if (mouseX > width - edgeMargin && mouseY < edgeMargin)
                mouseArea.cursorShape = Qt.SizeBDiagCursor;  // Angolo in alto a destra
               else if (mouseX < edgeMargin)
                mouseArea.cursorShape = Qt.SizeHorCursor;  // Bordo sinistro
               else if (mouseX > width - edgeMargin)
                mouseArea.cursorShape = Qt.SizeHorCursor;  // Bordo destro
               else if (mouseY < edgeMargin)
                mouseArea.cursorShape = Qt.SizeVerCursor;  // Bordo superiore
               else if (mouseY > height - edgeMargin)
                mouseArea.cursorShape = Qt.SizeVerCursor;  // Bordo inferiore
               else
                mouseArea.cursorShape = Qt.ArrowCursor;  // Nessun bordo
             }

             onPositionChanged: (mouse) => {
                updateCursorShape(mouse.x, mouse.y);
             }

            onPressed: (mouse)=> {
               if (mouse.button == Qt.LeftButton) {
                  if (mouseX < edgeMargin && mouseY < edgeMargin)
                     appWindow.startSystemResize(Qt.TopLeftCorner);
                  else if (mouseX > width - edgeMargin && mouseY > height - edgeMargin)
                     appWindow.startSystemResize(Qt.BottomRightCorner);
                  else if (mouseX < edgeMargin && mouseY > height - edgeMargin)
                      appWindow.startSystemResize(Qt.BottomLeftCorner);
                  else if (mouseX > width - edgeMargin && mouseY < edgeMargin)
                      appWindow.startSystemResize(Qt.TopRightCorner);
                  else if (mouseX < edgeMargin)
                      appWindow.startSystemResize(Qt.LeftEdge);
                  else if (mouseX > width - edgeMargin)
                      appWindow.startSystemResize(Qt.RightEdge);
                  else if (mouseY < edgeMargin)
                      appWindow.startSystemResize(Qt.TopEdge);
                  else if (mouseY > height - edgeMargin)
                      appWindow.startSystemResize(Qt.BottomEdge);
                  else
                      appWindow.startSystemMove();
               }
            }
          }


      }



    Connections {
             target: outputRedirector
             function onNewOutput(msg) {
                            testo.text += msg + "\n"
                           }
                  }

     Component.onDestruction: {
       appWindow.x = windowSettings.savedX
       appWindow.y = windowSettings.savedY
       appWindow.width = windowSettings.savedWidth
       appWindow.height = windowSettings.savedHeight

     }

}
