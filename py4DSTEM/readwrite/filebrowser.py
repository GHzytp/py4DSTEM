# Reads 4D-STEM data

import h5py
import numpy as np
import hyperspy.api as hs
from ..process.datastructure import DataCube
from ..process.datastructure import DiffractionSlice, RealSlice
from ..process.datastructure import PointList, PointListArray
from ..process.datastructure import Metadata
from ..process.log import log


################### BEGIN FileBrowser CLASS ##################

class FileBrowser(object):

    def __init__(self, filepath, **kwargs):
        self.filepath = filepath
        self.is_py4DSTEM_file = is_py4DSTEM_file(self.filepath)
        if not self.is_py4DSTEM_file:
            print("Error: FileBrowser instance can't read {}, because it isn't recognized as a py4DSTEM file.".format(self.filepath))
        else:
            self.version = get_py4DSTEM_version(self.filepath)
            self.file = h5py.File(filepath, 'r')
            self.set_object_lookup_info()
            #self.N_logentries = self.get_N_logentries()

    ###### Open/close methods ######

    def open(self):
        self.file = h5py.File(self.filepath, 'r')

    def close(self):
        if 'file' in self.__dict__.keys():
            self.file.close()

    def reload(self):
        """
        Same as set_object_lookup_info() - to be used when the file associated with an existing
        FileBrowser changes.
        """
        self.set_object_lookup_info()

    ###### Setup methods #####

    def set_object_lookup_info(self):
        if self.version == (0,3):
            self.set_object_lookup_info_v0_3()
        elif self.version == (0,2):
            self.set_object_lookup_info_v0_2()
        else:
            print("Error: unknown py4DSTEM version {}.{}.".format(self.version[0],self.version[1]))

    def set_object_lookup_info_v0_3(self):
        self.N_datacubes = len(self.file['4DSTEM_experiment']['data']['datacubes'])
        self.N_diffractionslices = len(self.file['4DSTEM_experiment']['data']['diffractionslices'])
        self.N_realslices = len(self.file['4DSTEM_experiment']['data']['realslices'])
        self.N_pointlists = len(self.file['4DSTEM_experiment']['data']['pointlists'])
        self.N_pointlistarrays = len(self.file['4DSTEM_experiment']['data']['pointlistarrays'])
        self.N_dataobjects = np.sum([self.N_datacubes, self.N_diffractionslices, self.N_realslices, self.N_pointlists, self.N_pointlistarrays])

        self.dataobject_lookup_arr = []
        self.dataobject_lookup_arr += ['DataCube' for i in range(self.N_datacubes)]
        self.dataobject_lookup_arr += ['DiffractionSlice' for i in range(self.N_diffractionslices)]
        self.dataobject_lookup_arr += ['RealSlice' for i in range(self.N_realslices)]
        self.dataobject_lookup_arr += ['PointList' for i in range(self.N_pointlists)]
        self.dataobject_lookup_arr += ['PointListArray' for i in range(self.N_pointlistarrays)]
        self.dataobject_lookup_arr = np.array(self.dataobject_lookup_arr)

    def set_object_lookup_info_v0_2(self):
        if len(self.file['4DSTEM_experiment']['rawdatacube'])==0:
            self.N_rawdatacubes = 0
        else:
            self.N_rawdatacubes = 1
        self.N_datacubes = len(self.file['4DSTEM_experiment']['processing']['datacubes'])
        self.N_diffractionslices = len(self.file['4DSTEM_experiment']['processing']['diffractionslices'])
        self.N_realslices = len(self.file['4DSTEM_experiment']['processing']['realslices'])
        self.N_pointlists = len(self.file['4DSTEM_experiment']['processing']['pointlists'])
        self.N_pointlistarrays = len(self.file['4DSTEM_experiment']['processing']['pointlistarrays'])
        self.N_dataobjects = np.sum([self.N_rawdatacubes, self.N_datacubes, self.N_diffractionslices, self.N_realslices, self.N_pointlists, self.N_pointlistarrays])

        self.dataobject_lookup_arr = []
        self.dataobject_lookup_arr += ['RawDataCube' for i in range(self.N_rawdatacubes)]
        self.dataobject_lookup_arr += ['DataCube' for i in range(self.N_datacubes)]
        self.dataobject_lookup_arr += ['DiffractionSlice' for i in range(self.N_diffractionslices)]
        self.dataobject_lookup_arr += ['RealSlice' for i in range(self.N_realslices)]
        self.dataobject_lookup_arr += ['PointList' for i in range(self.N_pointlists)]
        self.dataobject_lookup_arr += ['PointListArray' for i in range(self.N_pointlistarrays)]
        self.dataobject_lookup_arr = np.array(self.dataobject_lookup_arr)

    ###### Display object info ######

    def show_dataobject(self, index):
        """
        Display the info about dataobject at index.
        Two verbosity levels are supported through the 'v' boolean.
        """
        info = self.get_dataobject_info(index)

        if info['type'] == 'RawDataCube':
            print("{:<8}: {:<50}".format('Type', info['type']))
            print("{:<8}: {:<50}".format('Name', info['name']))
            print("{:<8}: {:<50}".format('Shape', str(info['shape'])))
            print("{:<8}: {:<50}".format('Index', index))
        elif info['type'] == 'DataCube':
            print("{:<8}: {:<50}".format('Type', info['type']))
            print("{:<8}: {:<50}".format('Name', info['name']))
            print("{:<8}: {:<50}".format('Shape', str(info['shape'])))
            print("{:<8}: {:<50}".format('Index', index))
        elif info['type'] == 'DiffractionSlice':
            print("{:<8}: {:<50}".format('Type', info['type']))
            print("{:<8}: {:<50}".format('Name', info['name']))
            print("{:<8}: {:<50}".format('Depth', info['depth']))
            print("{:<8}: {:<50}".format('Slices', str(info['slices'])))
            print("{:<8}: {:<50}".format('Shape', str(info['shape'])))
            print("{:<8}: {:<50}".format('Index', index))
        elif info['type'] == 'RealSlice':
            print("{:<8}: {:<50}".format('Type', info['type']))
            print("{:<8}: {:<50}".format('Name', info['name']))
            print("{:<8}: {:<50}".format('Depth', info['depth']))
            print("{:<8}: {:<50}".format('Slices', str(info['slices'])))
            print("{:<8}: {:<50}".format('Shape', str(info['shape'])))
            print("{:<8}: {:<50}".format('Index', index))
        elif info['type'] == 'PointList':
            print("{:<8}: {:<50}".format('Type', info['type']))
            print("{:<8}: {:<50}".format('Name', info['name']))
            print("{:<8}: {:<50}".format('Length', str(info['length'])))
            print("{:<8}: {:<50}".format('Coords', str(info['coordinates'])))
            print("{:<8}: {:<50}".format('Index', index))
        elif info['type'] == 'PointListArray':
            print("{:<8}: {:<50}".format('Type', info['type']))
            print("{:<8}: {:<50}".format('Name', info['name']))
            print("{:<8}: {:<50}".format('Shape', str(info['shape'])))
            print("{:<8}: {:<50}".format('Coords', str(info['coordinates'])))
            print("{:<8}: {:<50}".format('Index', index))
        else:
            print("{:<8}: {:<50}".format('Type', info['type']))
            print("{:<8}: {:<50}".format('Name', info['name']))
            print("{:<8}: {:<50}".format('Index', index))

    def show_dataobjects(self, index=None, objecttype=None):
        if index is not None:
            self.show_dataobject(index)

        elif objecttype is not None:
            if objecttype == 'RawDataCube':
                self.show_rawdatacubes()
            elif objecttype == 'DataCube':
                self.show_datacubes()
            elif objecttype == 'DiffractionSlice':
                self.show_diffractionslices()
            elif objecttype == 'RealSlice':
                self.show_realslices()
            elif objecttype == 'PointList':
                self.show_pointlists()
            elif objecttype == 'PointListArray':
                self.show_pointlistarrays()
            else:
                print("Error: unknown objecttype {}.".format(objecttype))

        else:
            print("{:^8}{:^36}{:^20}".format('Index', 'Name', 'Type'))
            for index in range(self.N_dataobjects):
                info = self.get_dataobject_info(index)
                name = info['name']
                objecttype = info['type']
                print("{:^8}{:<36}{:<20}".format(index, name, objecttype))

    def show_rawdatacubes(self):
        if self.version==(0,2):
            if self.N_rawdatacubes == 0:
                print("No RawDataCubes present.")
            else:
                print("{:^8}{:^36}{:^20}".format('Index', 'Name', 'Shape'))
                for index in (self.dataobject_lookup_arr=='RawDataCube').nonzero()[0]:
                    info = self.get_dataobject_info(index)
                    name = info['name']
                    shape = info['shape']
                    print("{:^8}{:<36}{:^20}".format(index, name, str(shape)))
        else:
            print("RawDataCubes are not supported past v0.2.")

    def show_datacubes(self):
        if self.N_datacubes == 0:
            print("No DataCubes present.")
        else:
            print("{:^8}{:^36}{:^20}".format('Index', 'Name', 'Shape'))
            for index in (self.dataobject_lookup_arr=='DataCube').nonzero()[0]:
                info = self.get_dataobject_info(index)
                name = info['name']
                shape = info['shape']
                print("{:^8}{:<36}{:^20}".format(index, name, str(shape)))

    def show_diffractionslices(self):
        if self.N_diffractionslices == 0:
            print("No DiffractionSlices present.")
        else:
            print("{:^8}{:^36}{:^10}{:^20}".format('Index', 'Name', 'Depth', 'Shape'))
            for index in (self.dataobject_lookup_arr=='DiffractionSlice').nonzero()[0]:
                info = self.get_dataobject_info(index)
                name = info['name']
                depth = info['depth']
                shape = info['shape']
                print("{:^8}{:<36}{:^10}{:^20}".format(index, name, depth, str(shape)))

    def show_realslices(self):
        if self.N_realslices == 0:
            print("No RealSlices present.")
        else:
            print("{:^8}{:^36}{:^10}{:^20}".format('Index', 'Name', 'Depth', 'Shape'))
            for index in (self.dataobject_lookup_arr=='RealSlice').nonzero()[0]:
                info = self.get_dataobject_info(index)
                name = info['name']
                depth = info['depth']
                shape = info['shape']
                print("{:^8}{:<36}{:^10}{:^20}".format(index, name, depth, str(shape)))

    def show_pointlists(self):
        if self.N_pointlists == 0:
            print("No PointLists present.")
        else:
            print("{:^8}{:^36}{:^8}{:^24}".format('Index', 'Name', 'Length', 'Coordinates'))
            for index in (self.dataobject_lookup_arr=='PointList').nonzero()[0]:
                info = self.get_dataobject_info(index)
                name = info['name']
                length = info['length']
                coordinates = info['coordinates']
                print("{:^8}{:<36}{:^8}{:^24}".format(index, name, length, str(coordinates)))

    def show_pointlistarrays(self):
        if self.N_pointlistarrays == 0:
            print("No PointListArrays present.")
        else:
            print("{:^8}{:^36}{:^12}{:^24}".format('Index', 'Name', 'Shape', 'Coordinates'))
            for index in (self.dataobject_lookup_arr=='PointListArray').nonzero()[0]:
                info = self.get_dataobject_info(index)
                name = info['name']
                shape = info['shape']
                coordinates = info['coordinates']
                print("{:^8}{:<36}{:^8}{:^24}".format(index, name, shape, str(coordinates)))

    ###### Get dataobject info #####

    def get_dataobject_info(self, index):
        """
        Returns a dictionary containing information about the object at index.
        Dict keys includes 'name', 'type', and 'index'.
        The following additional keys are object type dependent:
            DataCube: 'shape'
            DiffractionSlice, RealSlice: 'depth', 'slices', 'shape'
            PointList: 'coordinates', 'length'
            PointListArray: 'coordinates', 'shape'
            RawDataCube (v0.2 only): 'shape'
        """
        if self.version == (0,3):
            return self.get_dataobject_info_v0_3(index)
        elif self.version == (0,2):
            return self.get_dataobject_info_v0_2(index)
        else:
            print("Error: unknown py4DSTEM version {}.{}.".format(self.version[0],self.version[1]))
            return None

    def get_dataobject_info_v0_3(self, index):
        """
        Returns a dictionary containing information about the object at index for files written
        by py4DSTEM v0.3.
        """
        objecttype, objectindex = self.get_object_lookup_info(index)

        if objecttype == 'DataCube':
            name = list(self.file['4DSTEM_experiment']['data']['datacubes'].keys())[objectindex]
            shape = self.file['4DSTEM_experiment']['data']['datacubes'][name]['datacube'].shape
            objectinfo = {'name':name, 'shape':shape, 'type':objecttype, 'index':index}
        elif objecttype == 'DiffractionSlice':
            name = list(self.file['4DSTEM_experiment']['data']['diffractionslices'].keys())[objectindex]
            depth = self.file['4DSTEM_experiment']['data']['diffractionslices'][name].attrs['depth']
            slices = list(self.file['4DSTEM_experiment']['data']['diffractionslices'][name].keys())
            slices.remove('dim1')
            slices.remove('dim2')
            shape = self.file['4DSTEM_experiment']['data']['diffractionslices'][name][slices[0]].shape
            objectinfo = {'name':name, 'depth':depth, 'slices':slices, 'shape':shape, 'type':objecttype, 'index':index}
        elif objecttype == 'RealSlice':
            name = list(self.file['4DSTEM_experiment']['data']['realslices'].keys())[objectindex]
            depth = self.file['4DSTEM_experiment']['data']['realslices'][name].attrs['depth']
            slices = list(self.file['4DSTEM_experiment']['data']['realslices'][name].keys())
            slices.remove('dim1')
            slices.remove('dim2')
            shape = self.file['4DSTEM_experiment']['data']['realslices'][name][slices[0]].shape
            objectinfo = {'name':name, 'depth':depth, 'slices':slices, 'shape':shape, 'type':objecttype, 'index':index}
        elif objecttype == 'PointList':
            name = list(self.file['4DSTEM_experiment']['data']['pointlists'].keys())[objectindex]
            coordinates = list(self.file['4DSTEM_experiment']['data']['pointlists'][name].keys())
            length = self.file['4DSTEM_experiment']['data']['pointlists'][name][coordinates[0]]['data'].shape[0]
            objectinfo = {'name':name, 'coordinates':coordinates, 'length':length, 'type':objecttype, 'index':index}
        elif objecttype == 'PointListArray':
            name = list(self.file['4DSTEM_experiment']['data']['pointlistarrays'].keys())[objectindex]
            coordinates = list(self.file['4DSTEM_experiment']['data']['pointlistarrays'][name]['0_0'].keys())
            i,j=0,0
            for key in list(self.file['4DSTEM_experiment']['data']['pointlistarrays'][name].keys()):
                i0,j0 = int(key.split('_')[0]),int(key.split('_')[1])
                i,j = max(i0,i),max(j0,j)
            shape = (i+1,j+1)
            objectinfo = {'name':name, 'coordinates':coordinates, 'shape':shape, 'type':objecttype, 'index':index}
        else:
            print("Error: unknown dataobject type {}.".format(objecttype))
            objectinfo = {'name':'unsupported', 'type':'unsupported', 'index':index}
        return objectinfo

    def get_dataobject_info_v0_2(self, index):
        """
        Returns a dictionary containing information about the object at index for files written
        by py4DSTEM v0..
        """
        objecttype, objectindex = self.get_object_lookup_info(index)

        if objecttype == 'RawDataCube':
            name = 'rawdatacube'
            shape = self.file['4DSTEM_experiment']['rawdatacube']['datacube'].shape
            objectinfo = {'name':name, 'shape':shape, 'type':objecttype, 'index':index}
        elif objecttype == 'DataCube':
            name = list(self.file['4DSTEM_experiment']['processing']['datacubes'].keys())[objectindex]
            shape = self.file['4DSTEM_experiment']['processing']['datacubes'][name]['datacube'].shape
            objectinfo = {'name':name, 'shape':shape, 'type':objecttype, 'index':index}
        elif objecttype == 'DiffractionSlice':
            name = list(self.file['4DSTEM_experiment']['processing']['diffractionslices'].keys())[objectindex]
            depth = self.file['4DSTEM_experiment']['processing']['diffractionslices'][name].attrs['depth']
            slices = list(self.file['4DSTEM_experiment']['processing']['diffractionslices'][name].keys())
            slices.remove('dim1')
            slices.remove('dim2')
            shape = self.file['4DSTEM_experiment']['processing']['diffractionslices'][name][slices[0]].shape
            objectinfo = {'name':name, 'depth':depth, 'slices':slices, 'shape':shape, 'type':objecttype, 'index':index}
        elif objecttype == 'RealSlice':
            name = list(self.file['4DSTEM_experiment']['processing']['realslices'].keys())[objectindex]
            depth = self.file['4DSTEM_experiment']['processing']['realslices'][name].attrs['depth']
            slices = list(self.file['4DSTEM_experiment']['processing']['realslices'][name].keys())
            slices.remove('dim1')
            slices.remove('dim2')
            shape = self.file['4DSTEM_experiment']['processing']['realslices'][name][slices[0]].shape
            objectinfo = {'name':name, 'depth':depth, 'slices':slices, 'shape':shape, 'type':objecttype, 'index':index}
        elif objecttype == 'PointList':
            name = list(self.file['4DSTEM_experiment']['processing']['pointlists'].keys())[objectindex]
            coordinates = list(self.file['4DSTEM_experiment']['processing']['pointlists'][name].keys())
            length = self.file['4DSTEM_experiment']['processing']['pointlists'][name][coordinates[0]]['data'].shape[0]
            objectinfo = {'name':name, 'coordinates':coordinates, 'length':length, 'type':objecttype, 'index':index}
        elif objecttype == 'PointListArray':
            name = list(self.file['4DSTEM_experiment']['processing']['pointlistarrays'].keys())[objectindex]
            coordinates = list(self.file['4DSTEM_experiment']['processing']['pointlistarrays'][name]['0_0'].keys())
            i,j=0,0
            for key in list(self.file['4DSTEM_experiment']['processing']['pointlistarrays'][name].keys()):
                i0,j0 = int(key.split('_')[0]),int(key.split('_')[1])
                i,j = max(i0,i),max(j0,j)
            shape = (i+1,j+1)
            objectinfo = {'name':name, 'coordinates':coordinates, 'shape':shape, 'type':objecttype, 'index':index}
        else:
            print("Error: unknown dataobject type {}.".format(objecttype))
            objectinfo = {'name':'unsupported', 'type':'unsupported', 'index':index}
        return objectinfo

    ###### Get dataobjects ######

    def get_object_lookup_info(self, index):
        objecttype = self.dataobject_lookup_arr[index]
        mask = (self.dataobject_lookup_arr == objecttype)
        objectindex = index - np.nonzero(mask)[0][0]

        return objecttype, objectindex

    def get_dataobject(self, dataobject):
        """
        If dataobject is an int, instantiates a DataObject corresponding to the .h5 data pointed to
        by this index.
        If dataobject is a string, instantiates a DataObject with a matching name in the .h5 file.
        """
        if self.version==(0,3):
            if isinstance(dataobject, int):
                return self.get_dataobject_v0_3(dataobject)
            elif isinstance(dataobject, str):
                return self.get_dataobject_by_name(dataobject)
            else:
                print("Error: dataobject parameter must be type int or str.")
                return None
        elif self.version==(0,2):
            return self.get_dataobject_v0_2(index)
        else:
            print("Error: unrecognized py4DSTEM version {}.{}.".format(self.version[0],self.version[1]))

    def get_dataobject_v0_3(self, index):
        """
        Instantiates a DataObject corresponding to the .h5 data pointed to by index.
        """
        objecttype, objectindex = self.get_object_lookup_info(index)
        info = self.get_dataobject_info(index)
        name = info['name']

        if objecttype == 'DataCube':
            shape = info['shape']
            R_Nx, R_Ny, Q_Nx, Q_Ny = shape
            data = np.array(self.file['4DSTEM_experiment']['data']['datacubes'][name]['datacube'])
            dataobject = DataCube(data=data, name=name)

        elif objecttype == 'DiffractionSlice':
            depth = info['depth']
            slices = info['slices']
            shape = info['shape']
            Q_Nx, Q_Ny = shape
            if depth==1:
                data = np.array(self.file['4DSTEM_experiment']['data']['diffractionslices'][name][slices[0]])
            else:
                data = np.empty((shape[0], shape[1], depth))
                for i in range(depth):
                    data[:,:,i] = np.array(self.file['4DSTEM_experiment']['data']['diffractionslices'][name][slices[i]])
            dataobject = DiffractionSlice(data=data, slicelabels=slices, Q_Nx=Q_Nx, Q_Ny=Q_Ny, name=name)

        elif objecttype == 'RealSlice':
            depth = info['depth']
            slices = info['slices']
            shape = info['shape']
            R_Nx, R_Ny = shape
            if depth==1:
                data = np.array(self.file['4DSTEM_experiment']['data']['realslices'][name][slices[0]])
            else:
                data = np.empty((shape[0], shape[1], depth))
                for i in range(depth):
                    data[:,:,i] = np.array(self.file['4DSTEM_experiment']['data']['realslices'][name][slices[i]])
            dataobject = RealSlice(data=data, slicelabels=slices, R_Nx=R_Nx, R_Ny=R_Ny, name=name)

        elif objecttype == 'PointList':
            coords = info['coordinates']
            length = info['length']
            coordinates = []
            data_dict = {}
            for coord in coords:
                dtype = type(self.file['4DSTEM_experiment']['data']['pointlists'][name][coord]['data'][0])
                coordinates.append((coord, dtype))
                data_dict[coord] = np.array(self.file['4DSTEM_experiment']['data']['pointlists'][name][coord]['data'])
            dataobject = PointList(coordinates=coordinates, name=name)
            for i in range(length):
                new_point = tuple([data_dict[coord][i] for coord in coords])
                dataobject.add_point(new_point)

        elif objecttype == 'PointListArray':
            shape = info['shape']
            coords = info['coordinates']
            coordinates = []
            for coord in coords:
                dtype = type(self.file['4DSTEM_experiment']['data']['pointlistarrays'][name]['0_0'][coord]['data'][0])
                coordinates.append((coord, dtype))
            dataobject = PointListArray(coordinates=coordinates, shape=shape, name=name)
            for i in range(shape[0]):
                for j in range(shape[1]):
                    pointlist = dataobject.get_pointlist(i,j)
                    data_dict = {}
                    for coord in coords:
                        data_dict[coord] = np.array(self.file['4DSTEM_experiment']['data']['pointlistarrays'][name]['{}_{}'.format(i,j)][coord]['data'])
                    for k in range(len(data_dict[coords[0]])):
                        new_point = tuple([data_dict[coord][k] for coord in coords])
                        pointlist.add_point(new_point)

        else:
            print("Unknown object type {}. Returning None.".format(objecttype))
            dataobject = None

        return dataobject

    def get_dataobject_v0_2(self, index):
        """
        Instantiates a DataObject corresponding to the .h5 data pointed to by index.
        """
        objecttype, objectindex = self.get_object_lookup_info(index)
        info = self.get_dataobject_info(index)
        name = info['name']

        if objecttype == 'RawDataCube':
            shape = info['shape']
            R_Nx, R_Ny, Q_Nx, Q_Ny = shape
            data = np.array(self.file['4DSTEM_experiment']['rawdatacube']['datacube'])

            dataobject = DataCube(data=data, name=name)

        elif objecttype == 'DataCube':
            shape = info['shape']
            R_Nx, R_Ny, Q_Nx, Q_Ny = shape
            data = np.array(self.file['4DSTEM_experiment']['processing']['datacubes'][name]['datacube'])
            dataobject = DataCube(data=data, name=name)

        elif objecttype == 'DiffractionSlice':
            depth = info['depth']
            slices = info['slices']
            shape = info['shape']
            Q_Nx, Q_Ny = shape
            if depth==1:
                data = np.array(self.file['4DSTEM_experiment']['processing']['diffractionslices'][name][slices[0]])
            else:
                data = np.empty((depth, shape[0], shape[1]))
                for i in range(depth):
                    data[i,:,:] = np.array(self.file['4DSTEM_experiment']['processing']['diffractionslices'][name][slices[i]])
            dataobject = DiffractionSlice(data=data, slicelabels=slices, Q_Nx=Q_Nx, Q_Ny=Q_Ny, name=name)

        elif objecttype == 'RealSlice':
            depth = info['depth']
            slices = info['slices']
            shape = info['shape']
            R_Nx, R_Ny = shape
            if depth==1:
                data = np.array(self.file['4DSTEM_experiment']['processing']['realslices'][name][slices[0]])
            else:
                data = np.empty((depth, shape[0], shape[1]))
                for i in range(depth):
                    data[i,:,:] = np.array(self.file['4DSTEM_experiment']['processing']['realslices'][name][slices[i]])
            dataobject = RealSlice(data=data, slicelabels=slices, R_Nx=R_Nx, R_Ny=R_Ny, name=name)

        elif objecttype == 'PointList':
            coords = info['coordinates']
            length = info['length']
            coordinates = []
            data_dict = {}
            for coord in coords:
                dtype = type(self.file['4DSTEM_experiment']['processing']['pointlists'][name][coord]['data'][0])
                coordinates.append((coord, dtype))
                data_dict[coord] = np.array(self.file['4DSTEM_experiment']['processing']['pointlists'][name][coord]['data'])
            dataobject = PointList(coordinates=coordinates, name=name)
            for i in range(length):
                new_point = tuple([data_dict[coord][i] for coord in coords])
                dataobject.add_point(new_point)

        elif objecttype == 'PointListArray':
            shape = info['shape']
            coords = info['coordinates']
            coordinates = []
            for coord in coords:
                dtype = type(self.file['4DSTEM_experiment']['processing']['pointlistarrays'][name]['0_0'][coord]['data'][0])
                coordinates.append((coord, dtype))
            dataobject = PointListArray(coordinates=coordinates, shape=shape, name=name)
            for i in range(shape[0]):
                for j in range(shape[1]):
                    pointlist = dataobject.get_pointlist(i,j)
                    data_dict = {}
                    for coord in coords:
                        data_dict[coord] = np.array(self.file['4DSTEM_experiment']['processing']['pointlistarrays'][name]['{}_{}'.format(i,j)][coord]['data'])
                    for k in range(len(data_dict[coords[0]])):
                        new_point = tuple([data_dict[coord][k] for coord in coords])
                        pointlist.add_point(new_point)

        else:
            print("Unknown object type {}. Returning None.".format(objecttype))
            dataobject = None

        return dataobject

    def get_dataobjects(self, indices):
        if indices=='all':
            indices = range(self.N_dataobjects)
        objects = []
        for index in indices:
            objects.append(self.get_dataobject(index))
        return objects

    def get_all_dataobjects(self):
        return self.get_dataobjects('all')

    def get_rawdatacubes(self):
        objects = []
        for index in (self.dataobject_lookup_arr=='RawDataCube').nonzero()[0]:
            objects.append(self.get_dataobject(index))
        return objects

    def get_datacubes(self):
        objects = []
        for index in (self.dataobject_lookup_arr=='DataCube').nonzero()[0]:
            objects.append(self.get_dataobject(index))
        return objects

    def get_diffractionslices(self):
        objects = []
        for index in (self.dataobject_lookup_arr=='DiffractionSlice').nonzero()[0]:
            objects.append(self.get_dataobject(index))
        return objects

    def get_realslices(self):
        objects = []
        for index in (self.dataobject_lookup_arr=='RealSlice').nonzero()[0]:
            objects.append(self.get_dataobject(index))
        return objects

    def get_pointlists(self):
        objects = []
        for index in (self.dataobject_lookup_arr=='PointList').nonzero()[0]:
            objects.append(self.get_dataobject(index))
        return objects

    def get_pointlistarrays(self):
        objects = []
        for index in (self.dataobject_lookup_arr=='PointListArray').nonzero()[0]:
            objects.append(self.get_dataobject(index))
        return objects

    def get_dataobject_by_name(self, name, exactmatch=True):
        objects = []
        for i in range(self.N_dataobjects):
            objectname = self.get_dataobject_info(i)['name']
            if exactmatch:
                if name == objectname:
                    objects.append(self.get_dataobject(i))
            else:
                if name in objectname:
                    objects.append(self.get_dataobject(i))
        if len(objects)==1:
            objects = objects[0]
        return objects

    ###### Log display and querry ######

    def get_N_logentries(self):
        return

###################### END FileBrowser CLASS #######################




################# Utility functions ################

def is_py4DSTEM_file(h5_file):
    """
    Accepts either a filepath or an open h5py File object. Returns true if the file was written by
    py4DSTEM.
    """
    if isinstance(h5_file, h5py._hl.files.File):
        if ('version_major' in h5_file.attrs) and ('version_minor' in h5_file.attrs) and (('4DSTEM_experiment' in h5_file.keys()) or ('4D-STEM_data' in h5_file.keys())):
            return True
        else:
            return False
    else:
        try:
            f = h5py.File(h5_file, 'r')
            result = is_py4DSTEM_file(f)
            f.close()
            return result
        except OSError:
            return False

def get_py4DSTEM_version(h5_file):
    """
    Accepts either a filepath or an open h5py File object. Returns true if the file was written by
    py4DSTEM.
    """
    if isinstance(h5_file, h5py._hl.files.File):
        version_major = h5_file.attrs['version_major']
        version_minor = h5_file.attrs['version_minor']
        return version_major, version_minor
    else:
        try:
            f = h5py.File(h5_file, 'r')
            result = get_py4DSTEM_version(f)
            f.close()
            return result
        except OSError:
            print("Error: file cannot be opened with h5py, and may not be in HDF5 format.")
            return (0,0)


################# Log functions ################

def show_log(filename):
    """
    Takes a filename as input, determines if it was written by py4DSTEM, and if it was prints
    the file's log.
    """
    print("Reading log for file {}...\n".format(filename))
    # Check if file was written by py4DSTEM
    try:
        h5_file = h5py.File(filename,'r')
        if is_py4DSTEM_file(h5_file):
            try:
                log_group = h5_file['log']
                for i in range(len(log_group.keys())):
                    key = 'log_item_'+str(i)
                    show_log_item(i, log_group[key])
                h5_file.close()
            except KeyError:
                print("Log cannot be read - HDF5 file has no log group.")
                h5_file.close()
        else:
            h5_file.close()
    except IOError:
        print("Log cannot be read - file is not an HDF5 file.")

def show_log_item(index, log_item):
    time = log_item.attrs['time'].decode('utf-8')
    function = log_item.attrs['function'].decode('utf-8')
    version = log_item.attrs['version']

    print("*** Log index {}, at time {} ***".format(index, time))
    print("Function: \t{}".format(function))
    print("Inputs:")
    for key,value in log_item['inputs'].attrs.items():
        if type(value)==np.bytes_:
            print("\t\t{}\t{}".format(key,value.decode('utf-8')))
        else:
            print("\t\t{}\t{}".format(key,value))
    print("Version: \t{}\n".format(version))






