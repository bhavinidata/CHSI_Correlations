import os

import pandas as pd
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, and_

from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


#################################################
# Database Setup
#################################################

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "") or "postgresql+psycopg2://postgres:changeme@localhost:5432/CHSI_db"
db = SQLAlchemy(app)


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(db.engine, reflect=True)

# Save references to each table
DemographicData = Base.classes.demographic_data
RiskfactorData = Base.classes.riskfactor_data

@app.route("/")
def index():
    """Return the homepage."""
    return render_template("index.html")

@app.route("/demographic_risk")
def demographic_risk():

    """Return a list of Demographic data."""
    results = db.session.query(DemographicData, RiskfactorData).join(RiskfactorData).filter(and_(DemographicData.state_fips_code == RiskfactorData.state_code, DemographicData.county_fips_code == RiskfactorData.county_code)).limit(10).all()
    print(results)

    # Create a dictionary entry for each row of metadata information
    all_demogr_riskfact_data = []
    for result in results:
        print(result.keys())
        Demographic_RiskFactorDatas = {}
        Demographic_RiskFactorDatas["state_fips_code"] = result.demographic_data.state_fips_code
        Demographic_RiskFactorDatas["chsi_state_name"] = result.demographic_data.chsi_state_name
        Demographic_RiskFactorDatas["county_fips_code"] = result.demographic_data.county_fips_code
        
        all_demogr_riskfact_data.append(Demographic_RiskFactorDatas)

    print(all_demogr_riskfact_data)
    return jsonify(all_demogr_riskfact_data)

# route to get demographic sand riskfactor data statewise
@app.route("/demog_riskfact_statewise")
def riskfactors():

    """Return a list of Riskfactor data."""
    results = db.session.query(DemographicData.state_fips_code,\
            DemographicData.chsi_state_name,\
            DemographicData.county_fips_code,\
            DemographicData.chsi_county_name,\
            DemographicData.chsi_state_abbr,\
            DemographicData.strata_id_number,\
            DemographicData.strata_determining_factors,\
            DemographicData.number_counties,\
            DemographicData.population_size,\
            DemographicData.poverty,\
            DemographicData.age_19_under,\
            DemographicData.age_19_64,\
            DemographicData.age_65_84,\
            DemographicData.age_85_and_over,\
            DemographicData.white,\
            DemographicData.black,\
            DemographicData.native_american,\
            DemographicData.asian,\
            DemographicData.hispanic,\
            RiskfactorData.riskfactor_id,\
            RiskfactorData.state_code, \
            RiskfactorData.county_code, \
            RiskfactorData.no_exercise, \
            RiskfactorData.few_fruit_veg, \
            RiskfactorData.obesity, \
            RiskfactorData.high_blood_pres, \
            RiskfactorData.smoker, \
            RiskfactorData.diabetes, \
            RiskfactorData.uninsured, \
            RiskfactorData.prim_care_phys_rate, \
            RiskfactorData.dentist_rate, \
            RiskfactorData.community_health_center_ind).filter(and_(DemographicData.state_fips_code == RiskfactorData.state_code, DemographicData.county_fips_code == RiskfactorData.county_code)).all()

    # convert query result to pandas dataframe
    demographic_riskfactor_df= pd.DataFrame(results, columns=["state_fips_code",
                "chsi_state_name",
                "county_fips_code",\
                "chsi_county_name",\
                "chsi_state_abbr",\
                "strata_id_number",\
                "strata_determining_factors",\
                "number_counties",\
                "population_size",\
                "poverty",\
                "age_19_under",\
                "age_19_64",\
                "age_65_84",\
                "age_85_and_over",\
                "white",\
                "black",\
                "native_american",\
                "asian",\
                "hispanic",\
                "riskfactor_id",\
                "state_code", \
                "county_code", \
                "no_exercise", \
                "few_fruit_veg", \
                "obesity", \
                "high_blood_pres", \
                "smoker", \
                "diabetes", \
                "uninsured", \
                "prim_care_phys_rate", \
                "dentist_rate", \
                "community_health_center_ind"])

    demographic_riskfactor_df.head()

    # group by state and agrregate necessary columns
    stategroup_demoRisk_df = demographic_riskfactor_df.groupby(["state_fips_code", "chsi_state_abbr", "chsi_state_name"]).agg({"poverty":"mean", "obesity":"mean", "few_fruit_veg": "mean", "no_exercise": "mean", "diabetes": "mean", "high_blood_pres": "mean", "prim_care_phys_rate": "mean"})

    # drop null values
    stategroup_demoRisk_df = stategroup_demoRisk_df.dropna(how="any")

    stategroup_demoRisk_df.reset_index(inplace=True)
    # round to 2 decimal points
    stategroup_demoRisk_df = stategroup_demoRisk_df.round(2)

    # convert to dictionary from pandas dataframe
    stateg_dict = stategroup_demoRisk_df.to_dict("records")
    print(stateg_dict)

    # Create a dictionary entry for each row of metadata information
    stateg_demogr_riskfactor_data = []
    for result in stateg_dict:
        print(result)
        Demographic_RiskFactorDatas = {}
        Demographic_RiskFactorDatas["state_fips_code"] = result["state_fips_code"]
        Demographic_RiskFactorDatas["chsi_state_name"] = result["chsi_state_name"]
        # Demographic_RiskFactorDatas["county_fips_code"] = result[2]
        # Demographic_RiskFactorDatas["chsi_county_name"] = result[3]
        Demographic_RiskFactorDatas["chsi_state_abbr"] = result["chsi_state_abbr"]
        # Demographic_RiskFactorDatas["strata_id_number"] = result[5]
        # Demographic_RiskFactorDatas["strata_determining_factors"] = result[6]
        # Demographic_RiskFactorDatas["number_counties"] = result[7]
        # Demographic_RiskFactorDatas["population_size"] = result[8]
        Demographic_RiskFactorDatas["poverty"] = result["poverty"]
        # Demographic_RiskFactorDatas["age_19_under"] = result[10]
        # Demographic_RiskFactorDatas["age_19_64"] = result[11]
        # Demographic_RiskFactorDatas["age_65_84"] = result[12]
        # Demographic_RiskFactorDatas["age_85_and_over"] = result[13]
        # Demographic_RiskFactorDatas["white"] = result[14]
        # Demographic_RiskFactorDatas["black"] = result[15]
        # Demographic_RiskFactorDatas["native_american"] = result[16]
        # Demographic_RiskFactorDatas["asian"] = result[17]
        # Demographic_RiskFactorDatas["hispanic"] = result[18]
        # Demographic_RiskFactorDatas["riskfactor_id"] = result[19]
        # Demographic_RiskFactorDatas["state_code"] = result[20]
        # Demographic_RiskFactorDatas["county_code"] = result[21]
        Demographic_RiskFactorDatas["no_exercise"] = result["no_exercise"]
        Demographic_RiskFactorDatas["few_fruit_veg"] = result["few_fruit_veg"]
        Demographic_RiskFactorDatas["obesity"] = result["obesity"]
        Demographic_RiskFactorDatas["high_blood_pres"] = result["high_blood_pres"]
        # Demographic_RiskFactorDatas["smoker"] = result[25]
        Demographic_RiskFactorDatas["diabetes"] = result["diabetes"]
        # Demographic_RiskFactorDatas["uninsured"] = result[27]
        Demographic_RiskFactorDatas["prim_care_phys_rate"] = result["prim_care_phys_rate"]
        # Demographic_RiskFactorDatas["dentist_rate"] = result[29]
        # Demographic_RiskFactorDatas["community_health_center_ind"] = result[30]
        
        stateg_demogr_riskfactor_data.append(Demographic_RiskFactorDatas)

        print(stateg_demogr_riskfactor_data)
    return jsonify(stateg_demogr_riskfactor_data)

@app.route("/demo_riskfactor_countywise/<state>")
def demo_riskfactor_countywise(state):

    """Return a list of Demographic data."""
    results = db.session.query(DemographicData.state_fips_code,\
            DemographicData.chsi_state_name,\
            DemographicData.county_fips_code,\
            DemographicData.chsi_county_name,\
            DemographicData.chsi_state_abbr,\
            DemographicData.strata_id_number,\
            DemographicData.strata_determining_factors,\
            DemographicData.number_counties,\
            DemographicData.population_size,\
            DemographicData.poverty,\
            DemographicData.age_19_under,\
            DemographicData.age_19_64,\
            DemographicData.age_65_84,\
            DemographicData.age_85_and_over,\
            DemographicData.white,\
            DemographicData.black,\
            DemographicData.native_american,\
            DemographicData.asian,\
            DemographicData.hispanic,\
            RiskfactorData.riskfactor_id,\
            RiskfactorData.state_code, \
            RiskfactorData.county_code, \
            RiskfactorData.no_exercise, \
            RiskfactorData.few_fruit_veg, \
            RiskfactorData.obesity, \
            RiskfactorData.high_blood_pres, \
            RiskfactorData.smoker, \
            RiskfactorData.diabetes, \
            RiskfactorData.uninsured, \
            RiskfactorData.prim_care_phys_rate, \
            RiskfactorData.dentist_rate, \
            RiskfactorData.community_health_center_ind).filter(and_(DemographicData.state_fips_code == RiskfactorData.state_code, DemographicData.county_fips_code == RiskfactorData.county_code)).filter(DemographicData.chsi_state_name == state).all()

    county_demog_riskfactor_df= pd.DataFrame(results, columns=["state_fips_code",
                "chsi_state_name",
                "county_fips_code",\
                "chsi_county_name",\
                "chsi_state_abbr",\
                "strata_id_number",\
                "strata_determining_factors",\
                "number_counties",\
                "population_size",\
                "poverty",\
                "age_19_under",\
                "age_19_64",\
                "age_65_84",\
                "age_85_and_over",\
                "white",\
                "black",\
                "native_american",\
                "asian",\
                "hispanic",\
                "riskfactor_id",\
                "state_code", \
                "county_code", \
                "no_exercise", \
                "few_fruit_veg", \
                "obesity", \
                "high_blood_pres", \
                "smoker", \
                "diabetes", \
                "uninsured", \
                "prim_care_phys_rate", \
                "dentist_rate", \
                "community_health_center_ind"])

    county_demog_riskfactor_df.head()
    
    # drop any null values
    county_demog_riskfactor_df = county_demog_riskfactor_df.dropna(how="any")
      # round to 2 decimal points
    county_demog_riskfactor_df = county_demog_riskfactor_df.round(2)
    # create dictionary from pandas dataframe
    countyg_dict = county_demog_riskfactor_df.to_dict("records")

    # Create a dictionary entry for each row of metadata information
    countyg_demogr_riskfactor_data = []
    for result in countyg_dict:
        # print(result.keys())
        Demographic_RiskFactorDatasByCounty = {}
        Demographic_RiskFactorDatasByCounty["state_fips_code"] = result["state_fips_code"]
        Demographic_RiskFactorDatasByCounty["chsi_state_name"] = result["chsi_state_name"]
        Demographic_RiskFactorDatasByCounty["county_fips_code"] = result["county_fips_code"]
        Demographic_RiskFactorDatasByCounty["chsi_county_name"] = result["chsi_county_name"]
        Demographic_RiskFactorDatasByCounty["chsi_state_abbr"] = result["chsi_state_abbr"]
        # Demographic_RiskFactorDatas["strata_id_number"] = result[5]
        # Demographic_RiskFactorDatas["strata_determining_factors"] = result[6]
        # Demographic_RiskFactorDatas["number_counties"] = result[7]
        # Demographic_RiskFactorDatas["population_size"] = result[8]
        Demographic_RiskFactorDatasByCounty["poverty"] = result["poverty"]
        # Demographic_RiskFactorDatas["age_19_under"] = result[10]
        # Demographic_RiskFactorDatas["age_19_64"] = result[11]
        # Demographic_RiskFactorDatas["age_65_84"] = result[12]
        # Demographic_RiskFactorDatas["age_85_and_over"] = result[13]
        # Demographic_RiskFactorDatas["white"] = result[14]
        # Demographic_RiskFactorDatas["black"] = result[15]
        # Demographic_RiskFactorDatas["native_american"] = result[16]
        # Demographic_RiskFactorDatas["asian"] = result[17]
        # Demographic_RiskFactorDatas["hispanic"] = result[18]
        # Demographic_RiskFactorDatas["riskfactor_id"] = result[19]
        # Demographic_RiskFactorDatas["state_code"] = result[20]
        # Demographic_RiskFactorDatas["county_code"] = result[21]
        Demographic_RiskFactorDatasByCounty["no_exercise"] = result["no_exercise"]
        Demographic_RiskFactorDatasByCounty["few_fruit_veg"] = result["few_fruit_veg"]
        Demographic_RiskFactorDatasByCounty["obesity"] = result["obesity"]
        Demographic_RiskFactorDatasByCounty["high_blood_pres"] = result["high_blood_pres"]
        # Demographic_RiskFactorDatas["smoker"] = result[25]
        Demographic_RiskFactorDatasByCounty["diabetes"] = result["diabetes"]
        # Demographic_RiskFactorDatas["uninsured"] = result[27]
        Demographic_RiskFactorDatasByCounty["prim_care_phys_rate"] = result["prim_care_phys_rate"]
        # Demographic_RiskFactorDatas["dentist_rate"] = result[29]
        # Demographic_RiskFactorDatas["community_health_center_ind"] = result[30]

        # Demographic_RiskFactorDatasByCounty["state_fips_code"] = result.demographic_data.state_fips_code
        # Demographic_RiskFactorDatasByCounty["chsi_state_name"] = result.demographic_data.chsi_state_name
        # Demographic_RiskFactorDatasByCounty["county_fips_code"] = result.demographic_data.county_fips_code
        # Demographic_RiskFactorDatasByCounty["chsi_county_name"] = result.demographic_data.chsi_county_name
        # Demographic_RiskFactorDatasByCounty["chsi_state_abbr"] = result.demographic_data.chsi_state_abbr
        # # Demographic_RiskFactorDatas["strata_id_number"] = result[5]
        # # Demographic_RiskFactorDatas["strata_determining_factors"] = result[6]
        # # Demographic_RiskFactorDatas["number_counties"] = result[7]
        # # Demographic_RiskFactorDatas["population_size"] = result[8]
        # Demographic_RiskFactorDatasByCounty["poverty"] = result.demographic_data.poverty
        # # Demographic_RiskFactorDatas["age_19_under"] = result[10]
        # # Demographic_RiskFactorDatas["age_19_64"] = result[11]
        # # Demographic_RiskFactorDatas["age_65_84"] = result[12]
        # # Demographic_RiskFactorDatas["age_85_and_over"] = result[13]
        # # Demographic_RiskFactorDatas["white"] = result[14]
        # # Demographic_RiskFactorDatas["black"] = result[15]
        # # Demographic_RiskFactorDatas["native_american"] = result[16]
        # # Demographic_RiskFactorDatas["asian"] = result[17]
        # # Demographic_RiskFactorDatas["hispanic"] = result[18]
        # # Demographic_RiskFactorDatas["riskfactor_id"] = result[19]
        # # Demographic_RiskFactorDatas["state_code"] = result[20]
        # # Demographic_RiskFactorDatas["county_code"] = result[21]
        # Demographic_RiskFactorDatasByCounty["no_exercise"] = result.riskfactor_data.no_exercise
        # Demographic_RiskFactorDatasByCounty["few_fruit_veg"] = result.riskfactor_data.few_fruit_veg
        # Demographic_RiskFactorDatasByCounty["obesity"] = result.riskfactor_data.obesity
        # Demographic_RiskFactorDatasByCounty["high_blood_pres"] = result.riskfactor_data.high_blood_pres
        # # Demographic_RiskFactorDatas["smoker"] = result[25]
        # Demographic_RiskFactorDatasByCounty["diabetes"] = result.riskfactor_data.diabetes
        # # Demographic_RiskFactorDatas["uninsured"] = result[27]
        # Demographic_RiskFactorDatasByCounty["prim_care_phys_rate"] = result.riskfactor_data.prim_care_phys_rate
        # # Demographic_RiskFactorDatas["dentist_rate"] = result[29]
        # # Demographic_RiskFactorDatas["community_health_center_ind"] = result[30]
        
        countyg_demogr_riskfactor_data.append(Demographic_RiskFactorDatasByCounty)

        print(countyg_demogr_riskfactor_data)

    return jsonify(countyg_demogr_riskfactor_data)

if __name__ == "__main__":
    app.run(debug=True)