        #initialize query classes
        ROIQ = RegionsOfInterestQueries(self.dbase)
        AQ = AssessmentsQueries(self.dbase)
        RSQ = RadiotherapySessionsQueries(self.dbase)

        #create patient list
        masks = ROIQ.get_roi_names()
        module = 'dose'
        output = []
        i = 0
        v = False
        for key in patients:
            RTS_information = np.array(RSQ.get_session_ids(key).to_array())
            RTS_IDs = RTS_information[:,0]
            row = []
            for ID in RTS_IDs:
                print("Patient %f, %s"%(i, ID))
                dosegrid = RSQ.get_dose_grid(ID)
                valid = manager.runModule(dosegrid, module)
                row.append(valid)
            output.append(row)

        '''
            if ROI_ID is not None: # mask exists
                #print("Patient %f, Mask %f"%(i, j))
                tempmask = ROIQ.get_mask(ROI_ID)
                dosegrid = RSQ.get_dose_grid(patients[key])
                mask = DoseMask(tempmask, dosegrid).compute_dose_mask()

                if v is False:
                    print('visual start')
                    visual.visualize_mask(mask, None, None, 0.1)
                    v = True
                    print('visual done')

                valid = manager.runModule(mask, module)
                output[i][j] = valid
                #print("State: %f"%(output[i][j]))
                #print("Patient %f, Mask %f, State %f"%(i, j, output[i][j]))
            j = j + 1
        '''
