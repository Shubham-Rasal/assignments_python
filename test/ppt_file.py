
import win32com.client, sys, os
Application = win32com.client.Dispatch("PowerPoint.Application")
Application.Visible = True
Presentation = Application.Presendslides.Add(1, 12)
for Slide in Presentation.Slides:
     for Shape in Slide.Shapes:
             Shape.TextFrame.TextRange.Font.Name = "Arial"

Presentation.Save()
Application.Quit()