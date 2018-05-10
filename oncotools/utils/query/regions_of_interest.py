'''
This module contains a collection of predefined queries to interact with
the Oncospace database. These classes are all instantiated in the `Database`
class, for direct access to all the predefined procedures.
'''

import numpy as np

from ...data_elements.roi import Roi
from ...data_elements.dvh import Dvh

# RegionsOfInterest ======================================================


class RegionsOfInterestQueries(object):
    '''
    Queries on the `RegionsOfInterest` table.

    Positional arguments:
        :oncospace: Database class connected to an Oncospace database
    '''

    def __init__(self, oncospace):
        '''
        Initialize this class with a database connection
        '''
        self.oncospace = oncospace

    def get_roi_names(self, patientRepID=None):
        '''
        Get all region of interest (ROI) names.

        Returns:
            List of all ROI names
        '''
        where = '' if patientRepID is None else 'WHERE patientRepID={}'.format(patientRepID)
        queryString = '''
            SELECT DISTINCT name
            FROM RegionsOfInterest roi
            {}
            ORDER BY name'''.format(where)
        rois = self.oncospace.run(queryString)
        return [str(r[0]) for r in rois.rows]

    def get_id_by_patient_rep_id_name(self, patientRepID, roiName):
        '''
        Get ROI IDs by patientRepID and ROI name.

        Positional arguments:
            :patientRepID:  patient representation ID
            :roiName:       name of the region of interest
        Returns:
            :roiID:         ID of ROI associated with that patient
            :None:          if no ROI's were found
        Raises:
            :Exception:     if multiple ROI's were found
        '''
        queryString = """
            SELECT ID
            FROM RegionsOfInterest
            WHERE patientRepID = {0} AND name = '{1}'""".format(
                patientRepID, roiName)
        results = self.oncospace.run(queryString)
        if results.num_rows == 0:
            return None
        elif results.num_rows == 1:
            return results.rows[0][0]
        elif results.num_rows > 1:
            raise Exception('''Multiple ROI IDs were found
                for patientRepID "{0}" and ROI name "{1}"'''
                            .format(patientRepID, roiName))

    def get_ids_by_patient_rep_id_name(self, patientRepID, roiName):
        '''
        Get ROI IDs by patientRepID and ROI name.

        Positional arguments:
            :patientRepID:  patient representation ID
            :roiName:       name of the region of interest
        Returns:
            :roiID:         ID of ROI associated with that patient
            :None:          if no ROI's were found
        '''
        queryString = """
            SELECT ID
            FROM RegionsOfInterest
            WHERE patientRepID = {0} AND name = '{1}'""".format(
                patientRepID, roiName)
        results = self.oncospace.run(queryString)
        if results.num_rows == 0:
            return None
        return [row.ID for row in results.rows]

    def get_patient_rep_id(self, roiID):
        '''
        Get the patient representation ID corresponding to an ROI ID.

        Positional arguments:
            :roiID:     ROI ID
        Returns:
            Patient represetation corresponding to the ROI ID
        '''
        patientRepID = self.oncospace.run('''
            SELECT patientRepID
            FROM RegionsOfInterest
            WHERE ID = {0}'''.format(roiID))
        return int(patientRepID.rows[0][0])

    def get_patient_rep_ids_with_rois(self, rois):
        '''
        Get a list of patientRepID's that have ALL given ROIs

        Positional arguments:
            :rois:  a single ROI name or list of ROI names
        Returns:
            List of patient representation IDs with all ROIs
        '''
        # Make sure rois is a list
        if isinstance(rois, str):
            rois = [rois]
        # Format query
        if len(rois) == 1:
            where = "name = '{}'".format(rois[0])
        else:
            where = "name = '" + "' OR name = '".join(rois) + "'"
        query = '''
            SELECT a.patientRepID
            FROM (
                SELECT patientRepID, COUNT(name) as name_count
                FROM RegionsOfInterest
                WHERE {}
                GROUP BY patientRepID
            ) a
            WHERE a.name_count = {}
            ORDER BY patientRepID;
        '''.format(where, str(len(rois)))
        # Run the query
        results = self.oncospace.run(query)
        # Format the output
        output = [r[0] for r in results.rows]
        return output

    def get_ids_by_name(self, names):
        '''
        Get ROI IDs by ROI name.

        Positional arguments:
            :name:  name (or list of names) of the ROI
        Returns:
            `Results` object with columns patientID,
            patientRepID, roiID, and roiName
        '''
        # Make sure rois is a list
        if isinstance(names, str):
            names = [names]
        queryString = """
            SELECT pr.patientID, roi.patientRepID, roi.ID as roiID, roi.name
            FROM PatientRepresentations pr
            INNER JOIN RegionsOfInterest roi on roi.patientRepID = pr.ID
            WHERE roi.name IN ('{0}')""".format("','".join(names))
        return self.oncospace.run(queryString)

    def get_mask_representation(self, patientRepID=None, roiID=None):
        '''
        Get the fields associated to a patient representation.

        Keyword arguments:
            :patientRepID:  patient representation
            :roiID:         region of interest ID
        Returns:
            Dictionary containing fields of a patient representation

            Keys:
                patientRepID\n
                patientID\n
                xStart, yStart, zStart\n
                xVoxelSize, yVoxelSize, zVoxelSize\n
                xDimension, yDimension, zDimension
        '''
        if patientRepID is None:
            if roiID is None:
                raise Exception('Error:\
                    RegionsOfInterestClass.get_mask_representation: \
                    either patientRepID or roiID must be specified')
            else:
                patientRepID = self.get_patient_rep_id(roiID)
        return self.oncospace.patient_representations.get_patient_representation(patientRepID)

    def get_mask_rle(self, roiID):
        '''
        Get a run-length encoded ROI binary mask.
        Returned in the same format as stored in Oncospace

        Positional arguments:
            :roiID:     region of interest ID
        Returns:
            Array of run-length encoded mask
        '''
        # NOTE: TEXTSIZE is set to 2GB to prevent truncation by FreeTDS
        queryString = """
            SET TEXTSIZE 2147483647;
            SELECT roi.ID, roi.name, len(roi.mask) as maskLength,
            roi.mask, substring(roi.mask,1024,1) as missingChar
            FROM RegionsOfInterest roi WHERE roi.ID = {0}""".format(roiID)

        result = self.oncospace.run(queryString).rows[0]
        if result[2] == len(result[3]):
            # Make sure len(roi.mask) matches length of the RLE mask...
            maskRLE = result[3]
        elif result[2] == 1 + len(result[3]):
            # ...because sometimes the 1024th character is missing
            maskRLE = result[3][:1023] + result[4] + result[3][1023:]
        else:
            msg = 'Binary mask length is {0} characters, '.format(result[2])
            msg += 'but only {0} characters were queried \
                from the database'.format(len(result[3]))
            raise Exception(msg)
        return maskRLE

    def get_roi(self, roiID=None, mask=None):
        '''
        Get an ROI object corresponding to a roiID.

        The only necessary parameter is the `roiID`.

        Keyword arguments:
            :roiID:     ID corresponding to the ROI mask
            :mask:      run-length-encoded representation of the ROI mask
        Returns:
            `roi` instance related to the roi ID
        '''
        if mask is None and roiID is None:
            raise Exception('Error in get_mask(): \
                either the roiID or mask must be specified')
        elif mask is None:
            mask = self.get_mask_rle(roiID)
        rep = self.get_mask_representation(roiID=roiID)

        r = Roi()
        dim = [rep['zDimension'], rep['yDimension'], rep['xDimension']]
        spacing = [rep['xVoxelSize'], rep['yVoxelSize'], rep['zVoxelSize']]
        origin = [rep['xStart'], rep['yStart'], rep['zStart']]
        r.run_length_decode(mask, dim)
        r.mask.set_spacing(spacing)
        r.mask.set_origin(origin)
        r.mask.update_end()
        return r

    def get_mask(self, roiID):
        '''
        Get an ROI object corresponding to a roiID.

        Positional arguments:
            :roiID:     ID corresponding to the ROI mask
        Returns:
            Mask associated with the roi ID
        '''
        r = self.get_roi(roiID)
        if r is not None:
            return r.mask
        return None

    def __get_rois_helper(self, prepID, regs, getMask):
        '''
        Helper method: Query a patient's ROIs
        Format as a dictionary mapping ROI name to Roi/Mask object(s)
        '''
        def __query_helper(self, prepID, reg, getMask=False):
            '''
            Helper method: Query an ROI or mask
            '''
            found = None
            try:
                # Get the ROI ID by name
                roiIDs = self.get_ids_by_patient_rep_id_name(prepID, reg)
                # If there's only one, query it
                if len(roiIDs) == 1:
                    r = self.get_roi(roiIDs[0])
                    found = r.mask if getMask else r
                # If there are multiple, query all and store as a list
                elif len(roiIDs) > 1:
                    found = []
                    for roiID in roiIDs:
                        r = self.get_roi(roiID)
                        found.append(r.mask if getMask else r)
                return found
            except:
                return None

        masks = {}
        not_found = []
        if isinstance(regs, str):
            regs = [regs]
        for reg in regs:
            ret = __query_helper(self, prepID, reg, getMask=getMask)
            if ret is not None:
                masks[reg] = ret
            else:
                not_found.append(reg)
        return masks, not_found

    def get_rois(self, prepID, regs):
        '''
        Query a patient's ROIs

        Positional arguments:
            :prepID:    patient representation ID
            :regs:      ROI name, or list of ROI names
        Returns:
            :masks:     dictionary with ROI name (key) and Rois (value)
            :not_found: list of ROIs that were not found
        '''
        return self.__get_rois_helper(prepID, regs, False)

    def get_masks(self, prepID, regs):
        '''
        Query a patient's ROIs

        Positional arguments:
            :prepID:    patient representation ID
            :regs:      ROI name, or list of ROI names
        Returns:
            :masks:     dictionary with ROI name (key) and Masks (value)
            :not_found: list of ROIs that were not found
        '''
        return self.__get_rois_helper(prepID, regs, True)

    def get_dvh(self,
                doseSummaryID=None,
                rtSessionID=None,
                roiID=None,
                cumulative=True):
        '''
        Query for a DVH and construct a `dvh` object with that data.

        Keyword arguments:
            :doseSummaryID: doseSummaryID
            :rtSessionID:   radiotherapySessionID
            :roiID:         regionOfInterestID
            :cumulative:    True/False for cumulative or differential DVH
        Returns:
            `dvh` object with data queried from database
        '''
        queryString = '''
            SELECT X, Y
            FROM DVHData dvh
            JOIN RoiDoseSummaries rds ON rds.ID = dvh.roiDoseSummaryID'''
        if doseSummaryID is not None:
            queryString += 'where rds.ID = {0}'.format(doseSummaryID)
        elif rtSessionID is not None and roiID is not None:
            queryString += 'where rds.radiotherapySessionID = {0} \
                and rds.roiID = {1}'.format(rtSessionID, roiID)
        else:
            raise Exception('Error in query.RegionsOfInterestClass.get_dvh: \
                either the doseSummaryID \
                or both rtSessionID and roiID must be specified')

        if cumulative:
            queryString += " and rds.type = 'Cumulative DVH, Norm Volume'"
        else:
            queryString += " and rds.type = 'Differential DVH'"

        points = np.array(self.oncospace.run(queryString).rows)
        d = Dvh()
        d.set_data(points)
        if cumulative:
            d.dose_type = 'cum'
            d.dose_units = 'cGy'
            d.volume_type = 'cum'
            d.volume_units = 'normalized'
        else:
            d.dose_type = 'cum'
            d.dose_units = 'cGy'
            d.volume_type = 'diff'
            d.volume_units = 'cm3'
        return d
