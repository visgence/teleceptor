from django.contrib import admin
from .models import SensorReading, MessageQueue, Message, Sensor, DataStream, Path, Calibration

class SensorReadingAdmin(admin.ModelAdmin):
    exclude = ['id']

admin.site.register(SensorReading, SensorReadingAdmin)

class MessageQueueAdmin(admin.ModelAdmin):
    pass

admin.site.register(MessageQueue, MessageQueueAdmin)


class MessageAdmin(admin.ModelAdmin):
    pass

admin.site.register(Message, MessageAdmin)


class SensorAdmin(admin.ModelAdmin):
    pass

admin.site.register(Sensor, SensorAdmin)


class DataStreamAdmin(admin.ModelAdmin):
    pass

admin.site.register(DataStream, DataStreamAdmin)


class PathAdmin(admin.ModelAdmin):
    pass

admin.site.register(Path, PathAdmin)


class CalibrationAdmin(admin.ModelAdmin):
    pass

admin.site.register(Calibration, CalibrationAdmin)
