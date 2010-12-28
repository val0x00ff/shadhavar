# Copyright (C) 2010 Devnox-IT, http://www.devnox-it.com 
#
# Authors:
#     * Bert Desmet <bert@devnox-it.com>
#     * Bas Pape <basambora@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.




from django.db import models

class Datacentre(models.Model):
    class Meta:
        verbose_name_plural = "Datacenters"
        
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    postcode = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    comments = models.TextField(blank=True)

    def __unicode__(self):
        return unicode(self.name)

class Serverroom(models.Model):
    class Meta:
        verbose_name_plural = "Serverrooms"
        
    datacentre = models.ForeignKey(Datacentre, verbose_name="the datacentre this room is located")
    name = models.CharField(max_length=255)
    floor = models.PositiveIntegerField()
    maxrows = models.PositiveIntegerField()
    maxcolumns = models.PositiveIntegerField()
    comments = models.TextField(blank=True)

    def __unicode__(self):
        return unicode(self.name)

class Rack(models.Model):
    KIND_CHOICES = (
        ('0', '19" rack'),
        ('1', '23" rack'),
        ('2', 'blade'),
    )
    
    class Meta:
        verbose_name_plural = "Racks"
        

    name = models.CharField(max_length=255)
    height = models.PositiveIntegerField()
    kind = models.CharField(max_length=1, choices=KIND_CHOICES)
    row = models.PositiveIntegerField()
    column = models.PositiveIntegerField()
    serverroom = models.ForeignKey(Serverroom, verbose_name="the room this rack is located")
    rack = models.ForeignKey('self', related_name='parent_rack', verbose_name="the rack this rack is in", blank=True, null=True) # recursive relationship

    def __unicode__(self):
        text = u'rack({0},{1})'.format(unicode(self.serverroom), self.row)
        return text

class Device(models.Model):
    class Meta:
        verbose_name_plural = "Devices"
        
    rack = models.ForeignKey(Rack, verbose_name="the rack this device is in")
    name = models.CharField(max_length=255)
    height = models.PositiveIntegerField() #in units
    position = models.PositiveIntegerField() # from bottom
    brand = models.CharField(max_length=255)
    brandType = = models.CharField(max_length=255)
    os = models.CharField(max_length=255, blank=True)
    cpu = models.CharField(max_length=255)
    ram = models.PositiveIntegerField() # in megabytes
    startdate = models.DateField(blank=True, null=True)
    enddate = models.DateField(blank=True, null=True)

    def __unicode__(self):
        text = u'device({0}, {1}, {2})'.format(unicode(self.rack), self.position, self.os)
        return text

class Router(Device):
    class Meta:
        verbose_name_plural = "Routers"
        
    functions = models.ManyToManyField(DeviceFunction)

    def __unicode__(self):
        text = u'router({0}, {1}, {2})'.format(unicode(self.rack), self.position, self.os)
        return text

class Server(Device):
    class Meta:
        verbose_name_plural = "Servers"
        
    functions = models.ManyToManyField(DeviceFunction)

    def __unicode__(self):
        text = u'server({0}, {1}, {2})'.format(unicode(self.rack), self.position, self.os)
        return text

class Switch(Device):
    class Meta:
        verbose_name_plural = "switches"


    def __unicode__(self):
        text = u'switch({0}, {1}, {2})'.format(unicode(self.rack), self.position, self.os)
        return text

class KVM(Device):
    class Meta:
        verbose_name_plural = "KVMs"


    def __unicode__(self):
        text = u'KVM({0}, {1}, {2})'.format(unicode(self.rack), self.position, self.os)
        return text

class UPS(Device):
    class Meta:
        verbose_name_plural = "UPSes"


    def __unicode__(self):
        text = u'UPS({0}, {1}, {2})'.format(unicode(self.rack), self.position, self.os)
        return text

class Other(Device):

    functions = models.ManyToManyField(DeviceFunction)

    def __unicode__(self):
        text = u'other({0}, {1}, {2})'.format(unicode(self.rack), self.position, self.os)
        return text

class PDU(Device):
    class Meta:
        verbose_name_plural = "PDUs"


    def __unicode__(self):
        text = u'PDU({0}, {1}, {2})'.format(unicode(self.rack), self.position, self.os)
        return text
        
class VM(Device):
    class Meta:
        verbose_name_plural = "VMs"
        
    server = models.ForeignKey(Server, verbose_name="the server this VM runs on")
    functions = models.ManyToManyField(DeviceFunction)

    def __unicode__(self):
        text = u'VM({0}, {1}, {2})'.format(unicode(self.rack), self.position, self.os)
        return text

class Subnet(models.Model):
    class Meta:
        verbose_name_plural = "Subnets"
        
    networkaddr4 = models.IPAddressField(blank=True)
    subnetaddr4 = models.IPAddressField(blank=True)
    broadcast4 = models.IPAddressField(blank=True)
    networkaddr6 = models.IPAddressField(blank=True)
    subnetaddr6 = models.IPAddressField(blank=True)
    lastip6 = models.IPAddressField(blank=True)

    def __unicode__(self):
        text = u'subnet({0}, {1}, {2}, {3}, {4}, {5})'.format(self.networkaddr4, self.subnetaddr4, self.broadcast4, self.networkaddr6, self.subnetaddr6, self.lastip6)

class NetworkHardInterface(models.Model):
    class Meta:
        verbose_name_plural = "NetworkHardInterfaces"
        
    kind = models.CharField(max_length=255)

    def __unicode__(self):
        return unicode(self.kind)


class Networkinterface(models.Model):
    class Meta:
        verbose_name_plural = "Networkinterfaces"
        
    device = models.ForeignKey(Device, verbose_name="the device this interface belongs to")
    subnet = models.ForeignKey(Subnet, verbose_name="the subnet this interface is in")
    kind = models.ForeignKey(NetworkHardInterface, verbose_name="the official type of the hardware port")
    name = models.CharField(max_length=255)
    ip4 = models.IPAddressField(blank=True)
    ip6 = models.IPAddressField(blank=True)
    gateway4 = models.IPAddressField(blank=True)
    gateway6 = models.IPAddressField(blank=True)

    def __unicode__(self):
        return unicode(self.name)
        
class DeviceFunction(models.Model):
    class Meta:
        verbose_name_plural = "DeviceFunctions"
        
    name = models.CharField(max_length=255) 

