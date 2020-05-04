# Created by Eben van Ellewee

from ..Script import Script

class Ender3Timelapse(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "Ender 3 Timelapse",
            "key": "Ender3Timelapse",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "first_gcode":
                {
                    "label": "GCODE for display position.",
                    "description": "Fast move to display position.",
                    "type": "str",
                    "default_value": "G0 X215 Y220 F9000"
                },
                "second_gcode":
                {
                    "label": "GCODE for triggering camera.",
                    "description": "Slow move to trigger camera switch.",
                    "type": "str",
                    "default_value": "G0 X217 Y220 F2000"
                },
                "pause_length":
                {
                    "label": "Pause length",
                    "description": "How long to wait (in ms) after shutter pressed.",
                    "type": "int",
                    "default_value": 700,
                    "minimum_value": 0,
                    "unit": "ms"
                },
                "enable_retraction":
                {
                    "label": "Enable retraction",
                    "description": "Retract the filament before moving the head",
                    "type": "bool",
                    "default_value": true
                },
                "retraction_distance":
                {
                    "label": "Retraction distance",
                    "description": "How much to retract the filament.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 5,
                    "enabled": "enable_retraction"
                },
                "enable_zhop":
                {
                    "label": "Enable Z hop",
                    "description": "Enable Z Hop",
                    "type": "bool",
                    "default_value": true
                },
                "zhop_distance":
                {
                    "label": "Z hop height",
                    "description": "How much to lift the printheat for moves.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 1,
                    "enabled": "enable_zhop"
                }
            }
        }"""

    def execute(self, data):
        first_gcode = self.getSettingValueByKey("first_gcode")
        second_gcode = self.getSettingValueByKey("second_gcode")
        pause_length = self.getSettingValueByKey("pause_length")
        enable_retraction = self.getSettingValueByKey("enable_retraction")
        retraction_distance = self.getSettingValueByKey("retraction_distance")
        enable_zhop = self.getSettingValueByKey("enable_zhop")
        zhop_distance = self.getSettingValueByKey("zhop_distance")



        gcode_to_append = ";Ender3Timelapse Begin\n"
        last_x = 0
        last_y = 0

        gcode_to_append += self.putValue(G = 91) + ";Switch to relative positioning\n"
        if enable_retraction:
            gcode_to_append += self.putValue(G = 1, F = 1800, E = -retraction_distance) + ";Retraction\n"
        gcode_to_append += self.putValue(G = 0, Z = zhop_distance) + ";Move Z axis up a bit\n"
        gcode_to_append += self.putValue(G = 90) + ";Switch back to absolute positioning\n"
        gcode_to_append += first_gcode + ";GCODE for the first position(display position)\n"
        gcode_to_append += second_gcode + ";GCODE for the second position(trigger position)\n"
        gcode_to_append += self.putValue(M = 400) + ";Wait for moves to finish\n"
        gcode_to_append += self.putValue(G = 4, P = pause_length) + ";Wait for camera\n"


        for idx, layer in enumerate(data):
            for line in layer.split("\n"):
                if self.getValue(line, "G") in {0, 1}:  # Track X,Y location.
                    last_x = self.getValue(line, "X", last_x)
                    last_y = self.getValue(line, "Y", last_y)
            # Check that a layer is being printed
            lines = layer.split("\n")
            for line in lines:
                if ";LAYER:" in line:
                    layer += gcode_to_append

                    layer += "G0 F9000 X%s Y%s\n" % (last_x, last_y)
                    layer += "G91;Switch to relative positioning\n"
                    layer += "G0 Z-%s;Move Z axis down a bit\n" % (zhop_distance)
                    layer += "G90;Switch back to absolute positioning\n"
                    layer += ";Ender3Timelapse End\n"
					
                    data[idx] = layer
                    break
        return data
