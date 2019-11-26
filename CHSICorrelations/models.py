from .app import db


class DemographicData(db.Model):
    __tablename__ = "demographic_data"
    state_fips_code = db.Column(db.Integer, primary_key=True)     
    chsi_state_name = db.Column(db.String(255))
    county_fips_code = db.Column(db.Integer, primary_key=True)
    chsi_county_name = db.Column(db.String(255))
    chsi_state_abbr = db.Column(db.String(255))
    strata_id_number =  db.Column(db.Integer)     
    strata_determining_factors = db.Column(db.String(255))
    number_counties =  db.Column(db.Integer)     
    population_size =  db.Column(db.Integer)     
    poverty = db.Column(db.Float)
    age_19_under = db.Column(db.Float)
    age_19_64 = db.Column(db.Float)
    age_65_84 = db.Column(db.Float)
    age_85_and_over = db.Column(db.Float)
    white = db.Column(db.Float)
    black = db.Column(db.Float)
    native_american = db.Column(db.Float)
    asian = db.Column(db.Float)
    hispanic = db.Column(db.Float)
    def __repr__(self):
        return '<DemographicData %r>' % (self.name)

class RiskfactorData(db.Model):
    __tablename__ = "riskfactor_data"
    riskfactor_id = db.Column(db.Integer, primary_key=True)
    state_code = db.Column(db.Integer)     
    county_code = db.Column(db.Integer)
    no_exercise = db.Column(db.Float)
    few_fruit_veg = db.Column(db.Float)
    obesity = db.Column(db.Float)
    high_blood_pres = db.Column(db.Float)
    smoker = db.Column(db.Float)
    diabetes = db.Column(db.Float)
    uninsured = db.Column(db.Float)
    prim_care_phys_rate = db.Column(db.Float)
    dentist_rate = db.Column(db.Float)
    community_health_center_ind = db.Column(db.Float)
    __table_args__ = (db.ForeignKeyConstraint([county_code, state_code],
                                           [DemographicData.county_fips_code, DemographicData.state_fips_code]),
                      {})

    def __repr__(self):
        return '<RiskfactorData %r>' % (self.name)