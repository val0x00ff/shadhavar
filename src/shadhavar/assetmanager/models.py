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
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    postcode = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)
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
    row = models.PositiveIntegerField(null=True)
    column = models.PositiveIntegerField(null=True)
    serverroom = models.ForeignKey(Serverroom, verbose_name="the room this rack is located")
    rack = models.ForeignKey('self', related_name='parent_rack', verbose_name="the rack this rack is in", blank=True, null=True) # recursive relationship
    comments = models.TextField(blank=True)

    def __unicode__(self):
        text = u'rack({0},{1})'.format(unicode(self.serverroom), self.row)
        return text

class Device(models.Model):
    class Meta:
        verbose_name_plural = "Devices"

    rack = models.ForeignKey(Rack, verbose_name="the rack this device is in")
    name = models.CharField(max_length=255)
    height = models.PositiveIntegerField(blank=True, null=True) #in units
    position = models.PositiveIntegerField(blank=True, null=True) # from bottom
    brand = models.CharField(max_length=255, blank=True)
    brandType = models.CharField(max_length=255, blank=True)
    serialnr = models.CharField(max_length=255, blank=True)
    os = models.CharField(max_length=255, blank=True)
    startdate = models.DateField(blank=True, null=True)
    enddate = models.DateField(blank=True, null=True) #r.i.p
    maintainance = models.BooleanField()
    comments = models.TextField(blank=True)

    def __unicode__(self):
        text = u'device({0}, {1}, {2})'.format(unicode(self.rack), self.position, self.os)
        return text

class DeviceFunction(models.Model):
    class Meta:
        verbose_name_plural = "DeviceFunctions"

    name = models.CharField(max_length=255, blank=True)

    def __unicode__(self):
        return unicode(self.name)

class Router(Device):
    class Meta:
        verbose_name_plural = "Routers"

    functions = models.ManyToManyField(DeviceFunction, null=True)
    cpu = models.CharField(max_length=255, blank=True)
    ram = models.PositiveIntegerField(blank=True, null=True) # in megabytes

    def __unicode__(self):
        text = u'router({0}, {1}, {2})'.format(unicode(self.rack), self.position, self.os)
        return text

class Server(Device):
    class Meta:
        verbose_name_plural = "Servers"

    functions = models.ManyToManyField(DeviceFunction, null=True)
    cpu = models.CharField(max_length=255, blank=True)
    ram = models.PositiveIntegerField(blank=True, null=True) # in megabytes
    gpu = models.CharField(max_length=255, blank=True)


    def __unicode__(self):
        text = u'server({0}, {1}, {2})'.format(unicode(self.rack), self.position, self.os)
        return text

class Switch(Device):
    KIND_CHOICES = (
        ('0', 'Layer 2'),
        ('1', 'Layer 3'),
    )

    class Meta:
        verbose_name_plural = "switches"

    kind = models.CharField(max_length=1, choices=KIND_CHOICES, blank=True)
    poe = models.BooleanField() #power of ethernet

    def __unicode__(self):
        text = u'switch({0}, {1}, {2})'.format(unicode(self.rack), self.position, self.os)
        return text

class KVM(Device):
    REMOTE_CHOICES = (
        ('0', 'no'),
        ('1', 'Local remote / USB'),
        ('2', 'KVM over IP'),
    )

    class Meta:
        verbose_name_plural = "KVMs"

    connections = models.ManyToManyField(Device, related_name='connected_devices')
    remote = models.CharField(max_length=1, choices=REMOTE_CHOICES)
    maxdevices = models.PositiveIntegerField(blank=True, null=True)

    def __unicode__(self):
        text = u'KVM({0}, {1}, {2})'.format(unicode(self.rack), self.position, self.os)
        return text

class UPS(Device):
    MONITORING_CHOICES = (
        ('0', 'RS-232 serial'),
        ('1', 'Ethernet'),
    )

    MANAGEMENT_CHOICES = (
        ('0', 'telnet'),
        ('1', 'SSH'),
        ('2', 'SNMP'),
        ('3', 'web page'),
    )

    class Meta:
        verbose_name_plural = "UPSes"

    power = models.FloatField() #VoltAmperes
    ammountbatteries = models.PositiveIntegerField(null=True)
    typebatteries = models.CharField(max_length=255, blank=True)
    monitoring = models.CharField(max_length=1, choices=MONITORING_CHOICES)
    management = models.CharField(max_length=1, choices=MANAGEMENT_CHOICES)

    def __unicode__(self):
        text = u'UPS({0}, {1}, {2})'.format(unicode(self.rack), self.position, self.os)
        return text

class Other(Device):

    functions = models.ManyToManyField(DeviceFunction)

    def __unicode__(self):
        text = u'other({0}, {1}, {2})'.format(unicode(self.rack), self.position, self.os)
        return text

class PDU(Device):
    MONITORING_CHOICES = (
        ('0', 'RS-232 serial'),
        ('1', 'Ethernet'),
    )

    MANAGEMENT_CHOICES = (
        ('0', 'telnet'),
        ('1', 'SSH'),
        ('2', 'SNMP'),
        ('3', 'web page'),
    )

    class Meta:
        verbose_name_plural = "PDUs"

    ammount = models.PositiveIntegerField() #ammount of outlets
    monitoring = models.CharField(max_length=1, choices=MONITORING_CHOICES)
    management = models.CharField(max_length=1, choices=MANAGEMENT_CHOICES)

    def __unicode__(self):
        text = u'PDU({0}, {1}, {2})'.format(unicode(self.rack), self.position, self.os)
        return text

class DiskArray(Device):
    ARRAY_CHOICES = (
        ('0', 'Network Attached Storage (NAS)'),
        ('1', 'Modular SAN array'),
        ('2', 'Monolithic SAN array'),
        ('3', 'Utillity Storage Array'),
        ('4', 'Storage Virtualization'),
    )

    CONNECTION_CHOICES = (
        ('0', 'Ethernet'),
        ('1', 'Fiberchannel'),
        ('2', 'Serial'),
    )

    class Meta:
        verbose_name_plural = "DiskArrays"

    maxDisks = models.PositiveIntegerField()
    arrayType = models.CharField(max_length=1, choices=ARRAY_CHOICES)
    connection = models.CharField(max_length=1, choices=CONNECTION_CHOICES)
    conntectTo = models.ForeignKey(Server, verbose_name="the server this diskarray is conntected to", blank=True, null=True)

class VM(Device):
    class Meta:
        verbose_name_plural = "VMs"

    server = models.ForeignKey(Server, verbose_name="the server this vm runs on")
    functions = models.ManyToManyField(DeviceFunction)
    hypervisor = models.CharField(max_length=255, blank=True)
    cpu = models.CharField(max_length=255, blank=True)
    ram = models.PositiveIntegerField(blank=True, null=True) # in megabytes

    def __unicode__(self):
        text = u'VM({0}, {1}, {2})'.format(unicode(self.rack), self.position, self.os)
        return text

class Subnet(models.Model):
    class Meta:
        verbose_name_plural = "Subnets"

    networkaddr4 = models.IPAddressField(null=True, blank=True)
    subnetaddr4 = models.IPAddressField(null=True, blank=True)
    broadcast4 = models.IPAddressField(null=True, blank=True)
    networkaddr6 = models.IPAddressField(null=True, blank=True)
    subnetaddr6 = models.IPAddressField(null=True, blank=True)
    lastip6 = models.IPAddressField(null=True, blank=True)

    def __unicode__(self):
        text = 'subnet({0}, {1}, {2}, {3}, {4}, {5})'.format(unicode(self.networkaddr4), unicode(self.subnetaddr4), unicode(self.broadcast4), unicode(self.networkaddr6), unicode(self.subnetaddr6), unicode(self.lastip6))
        return unicode(text)

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
    ip4 = models.IPAddressField(null=True, blank=True)
    ip6 = models.IPAddressField(null=True, blank=True)
    gateway4 = models.IPAddressField(null=True, blank=True)
    gateway6 = models.IPAddressField(null=True, blank=True)
    mac = models.CharField(max_length=255, blank=True)
    vlan = models.PositiveIntegerField(null=True) 
    management = models.BooleanField() #is this a management port?
    connectedTo = models.ForeignKey('self', related_name='Connected_to', verbose_name="the networkinterface  is connected too", blank=True, null=True) # recursive relationship

    def __unicode__(self):
        return unicode(self.name)

class RaidArray(models.Model):
    RAID_CHOICES = (
        ('0', 'Raid 0'),
        ('1', 'Raid 1'),
        ('2', 'Raid 2'),
        ('3', 'Raid 3'),
        ('4', 'Raid 4'),
        ('5', 'Raid 5'),
        ('6', 'Raid 6'),
        ('7', 'Raid 1+0'),
        ('8', 'Raid 0+1'),
        ('9', 'Raid 5+1 / 53'),
        ('10', 'JBOD'),
    )

    class Meta:
        verbose_name_plural = "RaidArrays"

    name = models.CharField(max_length=255)
    Size = models.FloatField(null=True)
    raidType = models.CharField(max_length=1, choices=RAID_CHOICES)

class Harddisk(models.Model):
    IDE_CHOICES = (
        ('0', 'PATA'),
        ('1', 'SATA'),
        ('2', 'SCSI'),
        ('3', 'SAS'),
    )

    class Meta:
        verbose_name_plural = "Harddisks"

    parent = models.ForeignKey(Device, verbose_name="the device this hard disk is placed in", null=True)
    size = models.FloatField(null=True) #in gigabytes
    ide = models.CharField(max_length=1, choices=IDE_CHOICES)
    array = models.ForeignKey(RaidArray, verbose_name="the raid array this disk belongs to", null=True)
    startdate = models.DateField(blank=True, null=True)
    enddate = models.DateField(blank=True, null=True) #warranty
    brand = models.CharField(max_length=255, blank=True)
    brandType = models.CharField(max_length=255, blank=True)
    serialnr = models.CharField(max_length=255, blank=True)

    def __unicode__(self):
        text = u'Harddisk({0}, {1}, {2})'.format(unicode(self.parent), self.size, self.serialnr)
        return text

class Partition(models.Model):
    class Meta:
        verbose_name_plural = "Partitions"

    parent = models.ForeignKey(Device, verbose_name="the device this hard disk is placed in")
    name = models.CharField(max_length=255)
    size = models.FloatField(null=True)
    lvm = models.BooleanField()

    def __unicode__(self):
        text = u'Partition({0}, {1})'.format(unicode(self.parent), self.size)
        return text

class Maintenance(models.Model):
    target = models.ForeignKey(Device, verbose_name="the device under maintenance")
    reason = models.CharField(max_length=255, blank=True)
    scheduled = models.BooleanField()
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
