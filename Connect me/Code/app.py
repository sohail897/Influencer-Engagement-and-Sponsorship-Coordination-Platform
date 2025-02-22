from flask import Flask,redirect,render_template,request,url_for,flash
from models_2 import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user


#-------------------configuration-------------------------
app=Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///manymanydata.sqlite3"
db.init_app(app)
app.app_context().push()
with app.app_context():
    # db.drop_all()
    db.create_all()  
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

# Home Route

@app.route('/')
def home():
    return render_template('home.html')

# Register route

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('User already exists try Login')
            return redirect(url_for('login'))
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        db.create_all()
        user = User(username=username,password=hashed_password, role=role)
        db.session.add(user)
        db.session.commit()
        if role == 'sponsor':
            sponsor_name = request.form['sponsor_name']
            industry = request.form['industry']
            budget = request.form['budget']
            new_sponsor = Sponsor(user_id=user.user_id, name=sponsor_name, industry=industry, budget=budget)
            db.session.add(new_sponsor)
        elif role == 'influencer':
            influencer_name = request.form['influencer_name']
            category = request.form['category']
            niche = request.form['niche']
            reach = request.form['reach']
            new_influencer = Influencer(user_id=user.user_id, name=influencer_name, category=category, niche=niche, reach=reach)
            db.session.add(new_influencer)
    

        db.session.commit()
        flash('User registered successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



#LOgin Route

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user:
          
            flag = Flag.query.filter_by(user_id=user.user_id).first()
            if flag:
                flash('Your account has been flagged and you cannot log in.', 'danger')
                return redirect(url_for('login'))

            if check_password_hash(user.password, password):
                login_user(user)
                if user.role == 'sponsor':
                    return redirect(url_for('sponsor_dashboard'))
                elif user.role == 'influencer':
                    return redirect(url_for('influencer_dashboard'))
                elif user.role == 'admin':
                    return redirect(url_for('admin_dashboard'))
        
        flash('Invalid username or password', 'danger')
        
    return render_template('login.html')



# logout the current user

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

# Route to Sponsor Dashboaard

@app.route('/sponsor_dashboard')
@login_required
def sponsor_dashboard():
    if current_user.role != 'sponsor':
        return redirect(url_for('login'))

    try:
        sponsor = Sponsor.query.filter_by(user_id=current_user.user_id).first()

        if sponsor:

            campaigns = Campaign.query.filter_by(sponsor_id=sponsor.sponsor_id).all()

            ad_requests = AdRequest.query.join(Campaign).filter(Campaign.sponsor_id == sponsor.sponsor_id).all()

            return render_template('sponsors.html', sponsor=sponsor, campaigns=campaigns, ad_requests=ad_requests)
        else:
            flash('Sponsor information not found.')
            return redirect(url_for('login'))

    except Exception as e:
        print(f"Error fetching sponsor data: {e}")
        flash('An error occurred while fetching sponsor data.')
        return redirect(url_for('login'))
    
# Route to Influencer Dashboaard, INfluencer routes

@app.route('/influencer_dashboard')
@login_required
def influencer_dashboard():
    if current_user.role != 'influencer':
        return redirect(url_for('login'))

    try:
        influencer = Influencer.query.filter_by(user_id=current_user.user_id).first()
        
        if not influencer:
            flash('Influencer information not found.', 'danger')
            return redirect(url_for('login'))
        
        public_campaigns = Campaign.query.filter_by(visibility='public').all()

        ad_requests = AdRequest.query.filter_by(influencer_id=influencer.influencer_id).all()
    
    except Exception as e:
        print(f"Error fetching influencer data: {e}")
        flash('An error occurred while loading the dashboard.', 'danger')
        return redirect(url_for('login'))
    
    return render_template('influencer.html', 
                           influencer=influencer, 
                           public_campaigns=public_campaigns, 
                           ad_requests=ad_requests)

# Edit the current INfluencers profile

@app.route('/influencer/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if current_user.role != 'influencer':
        return redirect(url_for('login'))

    influencer = Influencer.query.filter_by(user_id=current_user.user_id).first()

    if not influencer:
        flash('Influencer profile not found.', 'danger')
        return redirect(url_for('influencer_dashboard'))

    if request.method == 'POST':
        try:
            influencer.name = request.form['name']
            influencer.category = request.form['category']
            influencer.niche = request.form['niche']
            influencer.reach = request.form['reach']
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('influencer_dashboard'))
        
        except Exception as e:
            print(f"Error updating profile: {e}")
            flash('An error occurred while updating your profile.', 'danger')
            db.session.rollback()

    return render_template('edit_profile.html', influencer=influencer)

@app.route('/campaign/<int:campaign_id>', methods=['GET'])
@login_required
def view_campaign(campaign_id):

    campaign = Campaign.query.get_or_404(campaign_id)

    if campaign.visibility != 'public':
        flash("You are not authorized to view this campaign.", "danger")
        return redirect(url_for('influencer_dashboard'))

    return render_template('view_campaign.html', campaign=campaign)


#Ad Requests


@app.route('/infmanage_ad_requests')
@login_required
def infmanage_ad_requests():
    if current_user.role != 'influencer':
        flash('You are not authorized to manage ad requests.', 'danger')
        return redirect(url_for('index'))
    
    ad_requests = AdRequest.query.filter_by(influencer_id=current_user.influencer.influencer_id).all()
    return render_template('infmanage_ad_requests.html', ad_requests=ad_requests)
@app.route('/ad_requests')


@login_required
def view_ad_requests():
    if current_user.role != 'influencer':
        flash('You are not authorized to view ad requests.', 'danger')
        return redirect(url_for('index'))
    
    ad_requests = AdRequest.query.filter_by(influencer_id=current_user.influencer.influencer_id).all()
    return render_template('view_ad_requests.html', ad_requests=ad_requests)

@app.route('/ad_request/<int:ad_request_id>/accept', methods=['POST'])
@login_required
def accept_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if ad_request.influencer_id != current_user.influencer.influencer_id:
        flash('You are not authorized to accept this ad request.', 'danger')
        return redirect(url_for('view_ad_requests'))
    
    ad_request.status = 'Accepted'
    db.session.commit()
    flash('Ad request accepted successfully!', 'success')
    return redirect(url_for('infmanage_ad_requests'))

@app.route('/ad_request/<int:ad_request_id>/reject', methods=['POST'])
@login_required
def reject_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if ad_request.influencer_id != current_user.influencer.influencer_id:
        flash('You are not authorized to reject this ad request.', 'danger')
        return redirect(url_for('view_ad_requests'))
    
    ad_request.status = 'Rejected'
    db.session.commit()
    flash('Ad request rejected successfully!', 'success')
    return redirect(url_for('infmanage_ad_requests'))



#Admin Dashbaord


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash("You are not authorized to access this page.", "danger")
        return redirect(url_for('index'))

    flagged_user_ids = [flag.user_id for flag in Flag.query.all()]
    users = User.query.filter(~User.user_id.in_(flagged_user_ids)).all()
    
    campaigns = Campaign.query.all()
    ad_requests = AdRequest.query.all()
    flagged_users = Flag.query.all()  

    return render_template('admin.html', users=users, campaigns=campaigns, ad_requests=ad_requests, flagged_users=flagged_users)


@app.route('/admin/flag/<int:user_id>', methods=['POST'])
@login_required
def flag_user(user_id):
    if current_user.role != 'admin':
        flash("You are not authorized to flag users.", "danger")
        return redirect(url_for('admin_dashboard'))
    
    
    if not Flag.query.filter_by(user_id=user_id).first():
        flag = Flag(user_id=user_id, reason="Flagged by admin")
        db.session.add(flag)
        
        campaigns = Campaign.query.filter_by(sponsor_id=user_id).all()
        for campaign in campaigns:
            AdRequest.query.filter_by(campaign_id=campaign.campaign_id).delete()
            db.session.delete(campaign)
        
        db.session.commit()
        flash("User flagged and associated data removed successfully!", "success")
    else:
        flash("User is already flagged.", "info")
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/unflag/<int:user_id>', methods=['POST'])
@login_required
def unflag_user(user_id):
  
    if current_user.role != 'admin':
        flash("You are not authorized to unflag users.", "danger")
        return redirect(url_for('admin_dashboard'))
    
    
    flag = Flag.query.filter_by(user_id=user_id).first()
    if flag:
        db.session.delete(flag)
        db.session.commit()
        flash("User unflagged successfully!", "success")
    else:
        flash("User is not flagged.", "info")
    
    return redirect(url_for('admin_dashboard'))


#Sponsor Routes

@app.route('/manage_campaigns', methods=['GET', 'POST'])
@login_required
def manage_campaigns():
    if current_user.role != 'sponsor':
        return redirect(url_for('login'))
    
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        budget = request.form['budget']
        visibility = request.form['visibility']
        goals = request.form['goals']

        new_campaign = Campaign(
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
            visibility=visibility,
            goals=goals,
            sponsor_id=current_user.sponsor.sponsor_id
        )
        db.session.add(new_campaign)
        db.session.commit()
        flash('Campaign created successfully!', 'success')
        return redirect(url_for('manage_campaigns'))
    campaigns = Campaign.query.all()
    print(campaigns)
    return render_template('manage_campaigns.html', campaigns=campaigns)

@app.route('/campaign/<int:campaign_id>/update', methods=['GET', 'POST'])
@login_required
def update_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    
    if current_user.role == 'admin':
        pass
    elif current_user.role == 'sponsor':
      
        if campaign.sponsor_id != current_user.sponsor.sponsor_id:
            flash("You are not authorized to update this campaign.", "danger")
            return redirect(url_for('sponsor_dashboard'))
    else:
        
        flash("Invalid role.", "danger")
        return redirect(url_for('sponsor_dashboard'))

    if request.method == 'POST':
        campaign.name = request.form['name']
        campaign.description = request.form['description']
        campaign.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        campaign.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        campaign.budget = request.form['budget']
        campaign.visibility = request.form['visibility']
        campaign.goals = request.form['goals']
        
        db.session.commit()
        flash('Campaign updated successfully!', 'success')

        
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('sponsor_dashboard'))
     

    return render_template('update_campaign.html', campaign=campaign)

@app.route('/accept_request/<int:ad_request_id>', methods=['POST'])
@login_required
def accept_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    ad_request.status = 'Accepted'
    db.session.commit()
    flash('Request accepted.', 'success')
    return redirect(url_for('sponsor_dashboard'))


@app.route('/reject_request/<int:ad_request_id>', methods=['POST'])
@login_required
def reject_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    ad_request.status = 'Rejected'
    db.session.commit()
    flash('Request rejected.', 'success')
    return redirect(url_for('sponsor_dashboard'))




@app.route('/campaign/<int:campaign_id>/delete', methods=['POST'])
@login_required
def delete_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)

    if current_user.role == 'admin':
        pass
    elif current_user.role == 'sponsor':
        if campaign.sponsor_id != current_user.sponsor.sponsor_id:
            flash("You are not authorized to delete this campaign.", "danger")
            return redirect(url_for('sponsor_dashboard')) 
    else:
       
        flash("Invalid role.", "danger")
        return redirect(url_for('sponsor_dashboard')) 

   
    AdRequest.query.filter_by(campaign_id=campaign_id).delete()
    db.session.delete(campaign)
    db.session.commit()

    flash("Campaign deleted successfully!", "success")

  
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))

    else:
        return redirect(url_for('manage_campaigns')) 


@app.route('/create_ad_request', methods=['GET', 'POST'])
@login_required
def create_ad_request():
    if current_user.role != 'sponsor':
        flash('You are not authorized to create an ad request.', 'danger')
        return redirect(url_for('/'))
    
    if request.method == 'POST':
        campaign_id = request.form['campaign_id']
        influencer_id = request.form['influencer_id']
        messages = request.form['messages']
        requirements = request.form['requirements']
        payment_amount = request.form['payment_amount']

        new_ad_request = AdRequest(
            campaign_id=campaign_id,
            influencer_id=influencer_id,
            messages=messages,
            requirements=requirements,
            payment_amount=payment_amount,
            status='Pending'
        )
        db.session.add(new_ad_request)
        db.session.commit()
        flash('Ad request created successfully!', 'success')
        return redirect(url_for('sponsor_dashboard'))
    
    campaigns = Campaign.query.filter_by(sponsor_id=current_user.sponsor.sponsor_id).all()
    influencers = Influencer.query.all()  
    return render_template('create_ad_request.html', campaigns=campaigns, influencers=influencers)
    

@app.route('/ad_request/<int:ad_request_id>/update', methods=['GET', 'POST'])
@login_required
def update_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if current_user.sponsor is None or ad_request.campaign.sponsor_id != current_user.sponsor.sponsor_id:
        flash('You are not authorized to update this ad request.', 'danger')
        return redirect(url_for('sponsor_dashboard'))
    
    if request.method == 'POST':
        ad_request.messages = request.form['messages']
        ad_request.requirements = request.form['requirements']
        ad_request.payment_amount = request.form['payment_amount']
        ad_request.status="Pending"
        db.session.commit()
        flash('Ad request updated successfully!', 'success')
        return redirect(url_for('sponsor_dashboard'))
    
    campaigns = Campaign.query.filter_by(sponsor_id=current_user.sponsor.sponsor_id).all()
    influencers = Influencer.query.all()
    return render_template('update_ad_request.html', ad_request=ad_request, campaigns=campaigns, influencers=influencers)

@app.route('/ad_request/<int:ad_request_id>/delete', methods=['POST'])
@login_required
def delete_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if current_user.sponsor is None or ad_request.campaign.sponsor_id != current_user.sponsor.sponsor_id:
        flash('You are not authorized to delete this ad request.', 'danger')
        return redirect(url_for('sponsor_dashboard'))
    
    db.session.delete(ad_request)
    db.session.commit()
    flash('Ad request deleted successfully!', 'success')
    return redirect(url_for('sponsor_dashboard'))



@app.route('/request_campaign/<int:campaign_id>', methods=['POST'])
@login_required
def request_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)

    
    existing_request = AdRequest.query.filter_by(influencer_id=current_user.user_id, campaign_id=campaign_id).first()
    if existing_request:
        flash('You have already requested to join this campaign.', 'warning')
        return redirect(url_for('influencer_dashboard'))

    new_request = AdRequest(
        influencer_id=current_user.user_id,
        campaign_id=campaign_id,
        messages="",  
        requirements="", 
        payment_amount=0,  
        status='Pending' 
    )

   
    db.session.add(new_request)
    db.session.commit()

    flash('Request sent successfully!', 'success')
    return redirect(url_for('influencer_dashboard'))







# Route for search influencers

@app.route('/search_influencers', methods=['GET'])
@login_required
def search_influencers():
    query = request.args.get('query', '')

    
    search_results = Influencer.query.filter(
        (Influencer.name.ilike(f'%{query}%')) |
        (Influencer.category.ilike(f'%{query}%')) |
        (Influencer.niche.ilike(f'%{query}%')) 
    ).all()

    return render_template('searchresultsinf.html', search_results=search_results, query=query)




# Route to search for Campaigns

@app.route('/search', methods=['GET'])
@login_required
def search_campaigns():
    query = request.args.get('query', '')

    
    search_results = Campaign.query.filter(
        Campaign.name.ilike(f'%{query}%'),
        Campaign.visibility == 'public'
    ).all()

    return render_template('search_results.html', search_results=search_results, query=query)



if __name__=='__main__':
      app.run(debug=True,host='0.0.0.0', port=4565)