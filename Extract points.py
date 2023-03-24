#Author-pkoprov@ncsu.edu
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback


ui = adsk.core.UserInterface.cast(None)
handlers = []
selectedFace = []

# Create a function to extract points on the surface of an object
def extract_points_on_surface(selection):
    try:

        # Check if the entity is a BRepFace
        if selection.objectType == adsk.fusion.BRepFace.classType():
            if selection.geometry.objectType == adsk.core.Plane.classType():
                # Get the parameter ranges of the surface
                edges = selection.edges
                origin = edges[0].startVertex.geometry.asArray()
                U = edges[0].endVertex.geometry.asArray()
                V = edges[1].startVertex.geometry.asArray()

                drawPoints(origin, U)
                return
                

                for i in range(nPointsU+1):
                    point = [j[0]+i*j[1] for j in zip(origin, dxyzU)]
                    drawPoints(point)
                    # start = [i*coor for coor in origin]
                    # for j in range(nPointsV+1):
                    #     drawPoints(point)


            elif selection.geometry.objectType == adsk.core.Cylinder.classType():
                ui.messageBox("Cylinder")
                ui.messageBox(str(selection.geometry.origin.asArray()))
            elif selection.geometry.objectType == adsk.core.Sphere.classType():
                ui.messageBox("Sphere")
            elif selection.geometry.objectType == adsk.core.Cone.classType():
                ui.messageBox("Cone")
            elif selection.geometry.objectType == adsk.core.Torus.classType():
                ui.messageBox("Torus")
            elif selection.geometry.objectType == adsk.core.NurbsSurface.classType():
                ui.messageBox("NurbsSurface")
            elif selection.geometry.objectType == adsk.core.EllipticalCone.classType():
                ui.messageBox("EllipticalCone")
            elif selection.geometry.objectType == adsk.core.EllipticalCylinder.classType():
                ui.messageBox("EllipticalCylinder")
            else:
                ui.messageBox("Other")

            # Get the parameter ranges of the surface
            
            # uRange = evaluator.parametricRange()
            # vRange = evaluator.getParameterExtentsInV()

            # Divide the surface into a grid of points
            # uCount = 10
            # vCount = 10
            # uStep = (uRange[1] - uRange[0]) / uCount
            # vStep = (vRange[1] - vRange[0]) / vCount

            # # Loop through each point on the grid and get the corresponding point on the surface
            # points = []
            # for u in range(uCount):
            #     for v in range(vCount):
            #         uParam = uRange[0] + u * uStep
            #         vParam = vRange[0] + v * vStep
            #         point = evaluator.getPointAtParameter(uParam, vParam)
            #         points.append(point)

            # # Return the list of points on the surface
            # return points

        else:
            ui.messageBox('Please select a face.')

    except:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Create an event handler for the "commandCreated" event
class MyCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()


    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
            cmd = eventArgs.command
            cmd.isExecutedWhenPreEmpted = False
            inputs = cmd.commandInputs
            
            selectInput = inputs.addSelectionInput('SelectionEventsSample', 'Face', 'Please select a faces')
            selectInput.addSelectionFilter(adsk.core.SelectionCommandInput.Faces)
            selectInput.setSelectionLimits(1)
            
            # Connect to the command related events.
            executePreview = MyCommandExecuteHandler()
            cmd.executePreview.add(executePreview)
            handlers.append(executePreview) 

            onExecute = MyCommandExecuteHandler()
            cmd.execute.add(onExecute)
            handlers.append(onExecute)        

            onDestroy = MyCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            handlers.append(onDestroy)  

            onSelect = MySelectHandler()
            cmd.select.add(onSelect)
            handlers.append(onSelect) 
            
            onUnSelect = MyUnSelectHandler()
            cmd.unselect.add(onUnSelect)            
            handlers.append(onUnSelect) 
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class MyCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # when the command is done, terminate the script
            # this will release all globals which will remove all event handlers
            adsk.terminate()
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class MySelectHandler(adsk.core.SelectionEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            global selectedFace
            selectedFace = adsk.fusion.BRepFace.cast(args.selection.entity)
            if selectedFace:
                # ui.messageBox('Face selected')
                pass

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
                
class MyUnSelectHandler(adsk.core.SelectionEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # when the command is done, terminate the script
            # this will release all globals which will remove all event handlers
            adsk.terminate()
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Create an event handler for the "commandExecute" event
class MyCommandExecuteHandler(adsk.core.CommandEventHandler):

    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:

            # Extract points on the surface of the selected face
            points = extract_points_on_surface(selectedFace)

        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

    def stop(context):
        try:
            app = adsk.core.Application.get()
            ui  = app.userInterface
            
            # Delete the command definition.
            cmdDef = ui.commandDefinitions.itemById('SelectionEventsSample_Python')
            if cmdDef:
                cmdDef.deleteMe()            
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def drawPoints(start, end):
    # Get the active sketch. 
    app = adsk.core.Application.get()

    design = app.activeProduct
    # Get the root component of the active design.
    rootComp = design.rootComponent
    # Create a new sketch on the xy plane.
    sketches = rootComp.sketches;
    xyPlane = rootComp.xYConstructionPlane
    sketch = sketches.add(xyPlane)

    distance = sum(([(i[1]-i[0])**2 for i in zip(start, end)]))**0.5
    nPoints = int(distance/0.1)
    dxyz = [(i[1]-i[0])/nPoints for i in zip(start, end)]

def drawPoint(sketch, xyz):
    sketchPoints = sketch.sketchPoints
    point = adsk.core.Point3D.create(xyz[0], xyz[1], xyz[2])
    sketchPoint = sketchPoints.add(point)


def run(context):
    global ui
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        
        myCmdDef = ui.commandDefinitions.itemById('SelectionEventsSample_Python')
        if myCmdDef is None:
            myCmdDef = ui.commandDefinitions.addButtonDefinition('SelectionEventsSample_Python', 'Selection Events Sample', '', '')
        
        # Connect to the command created event.
        onCommandCreated = MyCommandCreatedHandler()
        myCmdDef.commandCreated.add(onCommandCreated)
        handlers.append(onCommandCreated)
        
        # Execute the command.
        myCmdDef.execute()

        # prevent this module from being terminate when the script returns, because we are waiting for event handlers to fire
        adsk.autoTerminate(False)


    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
