# Author-pkoprov@ncsu.edu
# Description-

import adsk.core
import adsk.fusion
import adsk.cam
import traceback


handlers = []
selectedFace = []

# Create a function to extract points on the surface of an object


def extract_points_on_surface(selection):
    try:

        # Check if the entity is a BRepFace
        if selection.objectType == adsk.fusion.BRepFace.classType():
            if selection.geometry.objectType == adsk.core.Plane.classType():
                # Get the parameter ranges of the surface
                centroid = selection.centroid.asArray()
                edges = selection.edges
                vertices = [edge.startVertex.geometry.asArray()
                            for edge in edges]

                global faceToken
                faceToken = selection.entityToken

                pointsOnFace(centroid, vertices)
                return

            elif selection.geometry.objectType == adsk.core.Cylinder.classType():
                (ret, origin, axis, radius) = selection.geometry.getData()
                ui.messageBox("return value: {};\norigin: {};\naxis: {};\nradius: {}".format(
                    ret, origin.asArray(), axis.asPoint().asArray(), radius))
                pointsOnFace(origin.asArray(), radius=radius)
                pointsOnFace(axis.asPoint().asArray(), radius=radius)
                return

            # elif selection.geometry.objectType == adsk.core.Sphere.classType():
            #     ui.messageBox("Sphere")
            # elif selection.geometry.objectType == adsk.core.Cone.classType():
            #     ui.messageBox("Cone")
            # elif selection.geometry.objectType == adsk.core.Torus.classType():
            #     ui.messageBox("Torus")
            # elif selection.geometry.objectType == adsk.core.NurbsSurface.classType():
            #     ui.messageBox("NurbsSurface")
            # elif selection.geometry.objectType == adsk.core.EllipticalCone.classType():
            #     ui.messageBox("EllipticalCone")
            # elif selection.geometry.objectType == adsk.core.EllipticalCylinder.classType():
            #     ui.messageBox("EllipticalCylinder")
            else:
                ui.messageBox("Other")

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

            selectInput = inputs.addSelectionInput(
                'Draw Points On Face', 'Face', 'Please select a faces')
            selectInput.addSelectionFilter(
                adsk.core.SelectionCommandInput.Faces)
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
            ui = app.userInterface

            # Delete the command definition.
            cmdDef = ui.commandDefinitions.itemById(
                'DrawPointsOnFace')
            if cmdDef:
                cmdDef.deleteMe()
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def pointsOnFace(centroid, vertices=None, radius=None):
    app = adsk.core.Application.get()

    design = app.activeProduct
    # Get the root component of the active design.
    rootComp = design.rootComponent
    # Create a new sketch on the xy plane.
    sketches = rootComp.sketches
    xyPlane = rootComp.xYConstructionPlane
    sketch = sketches.add(xyPlane)

    sketch.isComputeDeferred = True
    if sketch:
        # Get sketch points
        if radius == None:
            for i, vertex in enumerate(vertices):
                pointsOnLine(sketch, vertices[i-1], vertices[i])
            points = [str(point.geometry.asArray())
                      for point in sketch.sketchPoints]
            points = "\n".join(points[1:])

            with open("C:/Users\pkoprov/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/Scripts/Extract points/edge_points.csv", "w") as f:
                f.write("{}:\n{}".format(faceToken, points))

            for vertex in vertices:
                pointsOnLine(sketch, centroid, vertex)
            points = [str(point.geometry.asArray())
                      for point in sketch.sketchPoints]
            points = "\n".join(points[1:])

            with open("C:/Users\pkoprov/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/Scripts/Extract points/centroid_points.csv", "w") as f:
                f.write("{}:\n{}".format(faceToken, points))
        else:
            drawPoint(sketch, centroid)

        return True
    else:
        return False


def pointsOnLine(sketch, start, end):

    # Get the distance between the two points, the number of points and distance between them
    distance = sum(([(i[1]-i[0])**2 for i in zip(start, end)]))**0.5
    nPoints = int(distance/0.1)
    if nPoints == 0:
        return
    dxyz = [(i[1]-i[0])/nPoints for i in zip(start, end)]

    # Create sketch point
    for i in range(nPoints+1):
        xyz = [coor[0]+i*coor[1] for coor in zip(start, dxyz)]
        drawPoint(sketch, xyz)


def drawPoint(sketch, xyz):
    sketchPoints = sketch.sketchPoints
    point = adsk.core.Point3D.create(xyz[0], xyz[1], xyz[2])
    sketchPoint = sketchPoints.add(point)


def run(context):
    global ui, app, design, rootComp

    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        rootComp = design.rootComponent

        myCmdDef = ui.commandDefinitions.itemById(
            'DrawPointsOnFace')
        if myCmdDef is None:
            myCmdDef = ui.commandDefinitions.addButtonDefinition(
                'DrawPointsOnFace', 'Draw Points On Face', '', '')

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
