import os
import cgi
import re
import random

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.webapp import template

class Gene(db.Model):
    wbgeneId = db.StringProperty(indexed=True)
    status = db.StringProperty(choices=('open','done'))
    user = db.UserProperty()
 
class Gene2curate(db.Model):
    wbgeneId = db.StringProperty(indexed=True)
   
class GrabGene(webapp.RequestHandler):
    def get(self):
      id = self.request.get('wbgeneId',None)
      u = users.get_current_user()
   
      q = Gene.all()
      q.filter('wbgeneId = ',id)
      gene = q.get()
      error = ''

      if id is None: # not id passed through
            error = ''
      elif gene is None: # render error about non-existing gene
            error = '<font color="red">could not find '+id+'</font>'
      else: 
            error = 'found '+id
   
            # if gene is already taken then set taken = True 
            if gene.status == 'done':
                 error = '<font color="red">'+id+' is already taken</font>'

            else:
                 gene.status ='done'
                 gene.user   = u
                 gene.put()

            c = Gene2curate.all()
            c.filter('wbgeneId = ',id)
            needCuration = c.get()
            if needCuration is not None:
               needCuration.delete()

      # grab a random gene from the curation list
      c = Gene2curate.all()
      genes2curate = c.count()
      randomGene = 'all done'
      if genes2curate > 0:
         o = random.randint(0,genes2curate-1)
         randomGene = c.get(offset=o).wbgeneId

      email = 'unknown'
      if gene is not None and gene.user is not None:
         email = gene.user.email()
     
      # and render the data      
      template_values = {'gene': gene, 'status': error, 'user': email,'randomGene': randomGene}

      path = os.path.join(os.path.dirname(__file__), 'edit.html')
      self.response.out.write(template.render(path, template_values))

class ShowGene(webapp.RequestHandler):
    def get(self):
      u = users.get_current_user()
   
      q = Gene.all()
      q.filter('user = ',u)
      genes = q.fetch(None)
     
      # and render the data      
      template_values = {'genes': genes}

      path = os.path.join(os.path.dirname(__file__), 'show.html')
      self.response.out.write(template.render(path, template_values))


# needs some logic#
class GenenameServer(webapp.RequestHandler):
    def post(self):
        gene = Gene()
        greeting.view = self.request.get('content')
        
        greeting.put()
        self.redirect('/')

application = webapp.WSGIApplication(
                                     [('/get', GrabGene),
                                      ('/', GrabGene),
                                      ('/show',ShowGene)],
                                      debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
