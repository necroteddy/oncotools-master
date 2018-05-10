import pydicom
import numpy as np
import warnings
from datetime import datetime
from collections import OrderedDict

from ..data_elements.roi import Roi, Contour
from ..data_elements.image import Image, Mask

class DicomReader(object):
    '''
    Interpret a set of DICOM files into Pythonic and oncotools specific representations
    '''

    def __init__(self, file_list):
        # List of files
        self.file_list = file_list if isinstance(
            file_list, list) else [file_list]

        # Metadata
        self.metadata = {
            'mrn': None,
            'patient_name': None,
            'last_name': None,
            'first_name': None,
            'attending': None,
            'manufacturer': None
        }
        # DICOM data
        self.dicom_files = None
        # Structures
        self.structures = {}
        # Plans
        self.plans = []
        # Doses
        self.doses = []
        # Keep track of DICOM file modalities so that a minimum set of DICOM files can be required
        self.modalities = []

        # Flags: Keep track of states to improve efficiency
        self.flags = {
            'metadata': False,
            'loaded': False,
            'structures': False,
            'modalities': False
        }

        # Load DICOM files
        self.data = self.load_files()

        # Load metadata
        self.metadata = self.get_metadata()

    def __close_file(self, dcm_file):
        '''
        Utility method: close a file
        '''
        if isinstance(dcm_file, file):
            dcm_file.close()

    def quick_load_files(self):
        '''
        Only loads metadata from each file
        '''
        def __after_patient_id(tag, VR, length):
            return tag == (0x0010, 0x0030)

        modalities = []
        for dcm_file in self.file_list:
            try:
                ds = pydicom.filereader.read_partial(
                    dcm_file, stop_when=__after_patient_id, force=True)
                modality = str(ds.Modality)
                modalities.append(modality)
                # Close the file
                self.__close_file(dcm_file)
            except:
                continue

        # Get the unique set of DICOM file types
        self.modalities = set(modalities)

    def load_files(self):
        '''
        Read DICOM files into memory
        '''
        # If metadata was already extracted, return it
        if self.flags['loaded']:
            return self.data

        dcm_dict = OrderedDict()
        # Load every file
        for dcm_file in self.file_list:
            try:
                # Read the file
                dicomData = pydicom.dcmread(dcm_file, force=True)
                # Extract modality
                modality = str(dicomData.Modality)
                self.modalities.append(modality)
                uid = dicomData.SOPInstanceUID

                # Organize data by modality, then UID
                if not modality in dcm_dict:
                    dcm_dict[modality] = OrderedDict()
                if not uid in dcm_dict[modality]:
                    dcm_dict[modality][uid] = dicomData

                # Close the file
                self.__close_file(dcm_file)
            except Exception:
                continue
        # Get the unique set of DICOM file types
        self.modalities = list(set(self.modalities))

        # Save the leaves of 'data'
        self.dicom_files = [dcm_dict[modality][uid]
                            for modality in dcm_dict for uid in dcm_dict[modality]]

        # Note that the files have been loaded
        self.flags['loaded'] = True

        return dcm_dict

    def get_metadata(self):
        '''
        Extract some basic information about the patient (MRN, name, attending, etc.)
        '''
        # If metadata was already extracted, return it
        if self.flags['metadata']:
            return self.metadata

        # Otherwise, parse it out
        found_data = []
        for dicomData in self.dicom_files:
            try:
                if 'RT' in str(dicomData.Modality) or str(dicomData.Modality) == 'CT' or str(dicomData.Modality) == 'MR':
                    # Extract metadata from that file
                    my_meta = {
                        'mrn': getattr(dicomData, 'PatientID', None),
                        'patient_name': getattr(dicomData, 'PatientName', None),
                        'attending': getattr(dicomData, 'PhysiciansOfRecord', None),
                        'first_name': None,
                        'last_name': None
                    }
                    # Get the patient's first and last name, if possible
                    if my_meta['patient_name'] is not None:
                        split_name = my_meta['patient_name'].split('^')
                        if len(split_name) > 1:
                            self.metadata['last_name'] = split_name[0]
                            self.metadata['first_name'] = split_name[1]
                        else:
                            self.metadata['last_name'] = split_name
                            self.metadata['first_name'] = split_name
                    found_data.append(my_meta)
            except Exception:
                continue
        # Merge metadata that was found
        merged = {}
        if len(found_data) > 0:
            d = found_data[0]
            for k in d.keys():
                merged[k] = tuple(d[k] for d in found_data)
            for m in merged.keys():
                merged[m] = list(set([v for v in merged[m] if v is not None]))
                if len(merged[m]) > 1:
                    warnings.warn(
                        'Multiple values found for key: {}'.format(m), Warning)
                else:
                    merged[m] = merged[m][0] if len(merged[m]) == 1 else None
        # Merge into self.metadata
        for key in merged.keys():
            self.metadata[key] = merged[key]

        # Flag that metadata was extracted
        self.flags['metadata'] = True

        return self.metadata

    def get_dicom_data(self, modality=None, uid=None):
        '''
        Return DICOM data associated with the given modality and/or UID

        Keyword arguments:
            :modality:  (default=None) Specify a modality (ex. RTSTRUCT)
            :uid:       (default=None) Specify a DICOM UID
        '''
        if not self.flags['loaded']:
            self.data = self.load_files()

        if modality and uid:
            return self.data.get(modality, {}).get(uid, {})
        elif modality:
            return self.data.get(modality, {})
        elif uid:
            for dicomDataByUID in self.data.values():
                for id, dicomData in dicomDataByUID.items():
                    if id == uid:
                        return dicomData
            return {}
        else:
            return self.data
        return None

    def get_structures(self, names=None):
        '''
        Get ROI masks from the RTSTRUCT file 

        Keyword arguments:
            :names:  Only load structures with these names
        '''
        # Extract enough ROI info to run the TagTargets script. Do not process contour data here
        structures = {}
        dicomData = self.get_dicom_data(modality='RTSTRUCT')
        if not dicomData:
            return None

        # If name(s) were provided
        if names is not None:
            # Make sure it's a list
            get_names = [names] if not isinstance(names, list) else names

            # Check if any were previously loaded
            structures = {name: self.structures[name]
                          for name in get_names if name in self.structures}
            # Only load the names that are left
            load_names = [name for name in get_names if name not in structures]
        else:
            # If no names were given, move on...
            load_names = names

        # Iterate over each DICOM data element
        for uid, data in dicomData.items():
            for (structure, contourSeq) in zip(data.StructureSetROISequence, data.ROIContourSequence):
                r = Roi()
                r.name = structure.ROIName

                # Check if the structure needs to be loaded
                # If names is None, load everything
                if load_names is None or r.name in load_names:
                    # Process contour data
                    if 'ContourSequence' in contourSeq:
                        for c in contourSeq.ContourSequence:
                            if c.ContourGeometricType == 'CLOSED_PLANAR':
                                contour_points = np.array(
                                    c.ContourData).astype(np.float_)/10.0
                                r.add_contour(contour_points)

                    # Extra DICOM-specific fields
                    r.uid = [uid]
                    r.id = [structure.ROINumber]

                    duplicateRoiIndices = self.check_for_duplicate_rois(
                        r, structures.values())
                    if duplicateRoiIndices:
                        # Current structure is a duplicate. Add to existing structure
                        for idx in duplicateRoiIndices:
                            structures[idx].uid.append(uid)
                            structures[idx].id.append(structure.ROINumber)
                    elif len(r.contours) > 0:
                        structures[r.name] = r

        # Save any newly loaded structures to the class' structure dictionary
        for s in structures:
            if s not in self.structures:
                self.structures[s] = structures[s]

        return structures

    def check_for_duplicate_rois(self, newRoi, existingRoiList):
        '''
        Compare the newRoi against the existing list of ROIs to determine if any are exact matches.
        Compares ROI names, number of contours, and volumes.

        Returns a list of indices of existing ROIs that match the newRoi
        '''
        duplicateRoiIndices = []
        for i, roi in enumerate(existingRoiList):
            if roi.name == newRoi.name and len(roi.contours) == len(newRoi.contours):
                if roi.get_volume() == newRoi.get_volume():
                    duplicateRoiIndices.append(i)
        return duplicateRoiIndices

    def get_planning_ct(self, plan=None):
        '''
        Parse and return a single planning CT from the collection of DICOM CT slices.
        Where applicable, units of mm are automatically converted to cm
        '''
        # First check for DICOM CT data
        modality = 'CT'
        allCTData = self.get_dicom_data(modality)
        if allCTData is None or not allCTData:
            modality = 'MR'
            allCTData = self.get_dicom_data(modality)
            if not allCTData:
                return None

        # The list of CT slices appears to consistently be in the referenced RTSTRUCT file
        roiData = None
        if plan is not None:
            planData = self.get_dicom_data('RTPLAN', plan.uid)
            if planData is not None and 'ReferencedStructureSetSequence' in planData:
                roiUID = planData.ReferencedStructureSetSequence[0].ReferencedSOPInstanceUID
                roiData = self.get_dicom_data('RTSTRUCT', roiUID)

        # Get a list of CT slice UIDs. An exception is raised if multiple CT scans are included
        # in the current DICOM data directory and a single CT scan cannot be unambiguously
        # associated with the current plan
        ctUIDList = []
        if roiData:
            refFrame = roiData.ReferencedFrameOfReferenceSequence[0]
            study = refFrame.RTReferencedStudySequence[0]
            series = study.RTReferencedSeriesSequence[0]
            ctUIDList = [
                ctSlice.ReferencedSOPInstanceUID for ctSlice in series.ContourImageSequence]
        else:
            ctUIDDict = {}
            for ctUID, ctData in allCTData.items():
                study = ctData.StudyInstanceUID
                series = ctData.SeriesInstanceUID
                if not (study, series) in ctUIDDict:
                    ctUIDDict[(study, series)] = []
                ctUIDDict[(study, series)].append(ctUID)
            if len(ctUIDDict.keys()) == 1:
                ctUIDList = list(ctUIDDict.values())[0]
            else:
                raise Exception(
                    'Multiple CT images: Failed to unambiguously associate a single CT with the current plan.')

        # Sort the CT slice UIDs by slice position
        slice_pos = [float(self.get_dicom_data(
            uid=uid).ImagePositionPatient[2]) for uid in ctUIDList]
        slice_pos, ctUIDList = (list(x)
                                for x in zip(*sorted(zip(slice_pos, ctUIDList))))

        # Compute the slice thickness as the most common difference between adjacent slices. Should
        # be robust against missing slices, but this remains untested...
        # TODO: include the direction cosines for more accurate slice thickness calculation!
        slice_thicknesses = [slice_pos[i+1]-slice_pos[i]
                             for i in range(len(slice_pos)-1)]
        slice_thickness_counts = sorted(
            [(slice_thicknesses.count(t), t) for t in set(slice_thicknesses)], reverse=True)
        slice_thickness = slice_thickness_counts[0][1]

        # Process CT metadata
        ct = Image()
        ct.modality = modality
        ctData = self.get_dicom_data(uid=ctUIDList[0])
        ct.origin = np.array([float(o)
                              for o in ctData.ImagePositionPatient])/10.0
        ct.size = np.abs(
            np.array([float(s) for s in [ctData.Rows, ctData.Columns, len(ctUIDList)]]).astype(int))
        ct.direction = np.array([float(d)
                                 for d in ctData.ImageOrientationPatient])
        ct.spacing = [float(s)/10.0 for s in ctData.PixelSpacing]
        ct.spacing.append(slice_thickness/10.0)
        ct.update_end()

        # Load CT slices to the image
        ct.allocate()
        for z, ctUID in enumerate(ctUIDList):
            ct.data[z, :, :] = self.get_dicom_data(uid=ctUID).pixel_array

        # Extra DICOM info
        ct.study = ctData.StudyInstanceUID
        ct.series = ctData.SeriesInstanceUID
        if 'AcquisitionDate' in ctData and 'AcquisitionTime' in ctData:
            ct.datetime = datetime.strptime(
                (ctData.AcquisitionDate+ctData.AcquisitionTime)[:14], '%Y%m%d%H%M%S')
        else:
            ct.datetime = None

        return ct

    def get_binary_mask(self, structure, template=None, radius=0):
        '''
        Define how the binary mask is generated depending on the DICOM data source (Pinnacle, Tomo, etc.)
        '''
        if template is None:
            if len(self.plans) > 0:
                if hasattr(self.plans[0], 'planning_ct'):
                    template = self.plans[0].planning_ct
                else:
                    template = self.get_planning_ct(self.plans[0])
            else:
                template = self.get_planning_ct()

        # Pinnacle binary masks
        if self.metadata['manufacturer'] == 'ADAC':
            return self.get_pinnacle_binary_mask(structure, template)

        # Tomotherapy binary masks
        elif self.metadata['manufacturer'] == 'TomoTherapy Incorporated':
            return self.get_tomotherapy_binary_mask(structure, template)

        # Default options: use ADAC mask specification
        else:
            return self.get_pinnacle_binary_mask(structure, template, radius)

    def get_pinnacle_binary_mask(self, structure, template, radius=None):
        '''
        Compute a binary mask to match those from Pinnacle (as closely as possible). Differences
        between Pinnacle masks and the ones generated here commonly arise from:
        - Slight rounding errors for points near the edge between two voxels
        '''
        return structure.get_mask(template=template, radius=0.0001, map_points_to_voxels=True)

    def get_tomotherapy_binary_mask(self, structure, template):
        '''
        Compute a binary mask to match those from Tomotherapy (as closely as possible)
        '''
        mask = structure.get_edge_weighted_mask(
            template=template, radius=0.001)
        mask.data[mask.data > 0] = 1.0
        mask.data = mask.data.astype(np.dtype('b'))
        return mask
