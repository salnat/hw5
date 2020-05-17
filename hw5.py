import pathlib
import pandas as pd
from typing import Union,Tuple
import numpy as np
from matplotlib import pyplot as plt
import re
regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{1,3}$'

    
class QuestionnaireAnalysis:
    """
    Reads and analyzes data generated by the questionnaire experiment.
    Should be able to accept strings and pathlib.Path objects.
    """

    def __init__(self, data_fname: Union[pathlib.Path, str]):
        try:
            self.data_fname = pathlib.Path(data_fname).absolute()
        except TypeError: 
            print('Error!, Please enter a pathlib object or a string!')
        if not self.data_fname.exists():
            raise ValueError(f"File {str(self.data_fname)} doesn't exist.")
        

    def read_data(self):
        """Reads the json data located in self.data_fname into memory, to
        the attribute self.data.
        """
        self.data = pd.read_json(self.data_fname)
    def show_age_distrib(self) -> Tuple[np.ndarray, np.ndarray]:
        """Calculates and plots the age distribution of the participants.

            Returns
            -------
            hist : np.ndarray
            Number of people in a given bin
            bins : np.ndarray
            Bin edges
        """
        b = np.linspace(0,100,11)
        fig,ax = plt.subplots()
        hist,edges,_ = ax.hist(self.data['age'],bins=b)
        ax.set_title('Age Dist. in Dataset')
        ax.set_xlabel('Count')
        ax.set_ylabel('Age')
        return hist,edges

    def email_checker(self,mail):
        if (re.search(regex,mail)):  
            return True 
        else:
            return False
        
    def remove_rows_without_mail(self) -> pd.DataFrame:
        
        """
        Checks self.data for rows with invalid emails, and removes them.

        Returns
        -------
        df : pd.DataFrame
        A corrected DataFrame, i.e. the same table but with the erroneous rows removed and
        the (ordinal) index after a reset.
        """
        valid=self.data['email'].apply(lambda val: self.email_checker(val))
        return self.data.loc[valid].reset_index(drop=True)
    def fill_na_with_mean(self) -> Tuple[pd.DataFrame, np.ndarray]:
        """Finds, in the original DataFrame, the subjects that didn't answer
        all questions, and replaces that missing value with the mean of the
        other grades for that student.

        Returns
        -------
        df : pd.DataFrame
        The corrected DataFrame after insertion of the mean grade
        arr : np.ndarray
        Row indices of the students that their new grades were generated
        """
        grades = self.data.loc[:,'q1':'q5']
        new_grades=grades.apply(lambda x: x.fillna(x.mean()),axis=1)
        null_loc = grades.loc[grades.isna().any(axis=1)].index.to_numpy()
        full_data =  pd.concat([self.data.loc[:, :"last_name"], new_grades], axis=1)
        return full_data,null_loc
    def score_subjects(self, maximal_nans_per_sub: int = 1) -> pd.DataFrame:
        """Calculates the average score of a subject and adds a new "score" column
        with it.

        If the subject has more than "maximal_nans_per_sub" NaN in his grades, the
        score should be NA. Otherwise, the score is simply the mean of the other grades.
        The datatype of score is UInt8, and the floating point raw numbers should be
        rounded down.

        Parameters
        ----------
        maximal_nans_per_sub : int, optional
            Number of allowed NaNs per subject before giving a NA score.

        Returns
        -------
        pd.DataFrame
            A new DF with a new column - "score".
        """
        grades=self.data.loc[:,'q1':'q5']
        grades['num_nan']=grades.isnull().sum(axis=1)
        grades['Score'] = grades.mean(axis=1)
        grades.loc[(grades.num_nan>maximal_nans_per_sub),'Score']= float('NaN')
        grades.drop(['num_nan'],axis=1)
        data_with_score =  pd.concat([self.data.loc[:, :"last_name"], grades], axis=1)
        return data_with_score
        