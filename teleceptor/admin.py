from django.contrib import admin
from .models import SensorReading, MessageQueue, Message, Sensor, DataStream, Path, Calibration

class SensorReadingAdmin(admin.ModelAdmin):
    exclude = ['id']
    list_display = ['id', 'datastream','sensor','timestamp', 'value']
    list_filter = ['sensor']

admin.site.register(SensorReading, SensorReadingAdmin)

class MessageQueueAdmin(admin.ModelAdmin):
    pass

admin.site.register(MessageQueue, MessageQueueAdmin)


class MessageAdmin(admin.ModelAdmin):
    pass

admin.site.register(Message, MessageAdmin)


class SensorAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'name', 'units', 'model', 'last_calibration']

admin.site.register(Sensor, SensorAdmin)


class DataStreamAdmin(admin.ModelAdmin):
    list_display = ['id', 'sensor', 'name','min_value', 'max_value']


admin.site.register(DataStream, DataStreamAdmin)


class PathAdmin(admin.ModelAdmin):
    list_display = ['id', 'datastream', 'path' ]

admin.site.register(Path, PathAdmin)


class CalibrationAdmin(admin.ModelAdmin):
    list_display = ['id', 'sensor', 'timestamp', 'coefficients' ]

admin.site.register(Calibration, CalibrationAdmin)
