# -*- coding: utf-8 -*-

from odoo import models, fields, api, Command
import tensorflow as tf

class Exercise(models.Model):
    _name = 'ml_learning.exercise'
    _description = 'ml_learning.exercise'
    _rec_name = 'id'

    question = fields.Char("Pregunta")

    answer_1 = fields.Char("Respuesta 1")

    answer_2 = fields.Char("Respuesta 2")

    answer_3 = fields.Char("Respuesta 3")

    answer_4 = fields.Char("Respuesta 4")

    correct_answer = fields.Char("Respuesta Correcta")

    intelligence_type = fields.Selection([
        ('math','Matematica'),
        ('linguistic','Linguistica'),
        ('interpersonal','Interpersonal'),
        ('intrapersonal','Intrapersonal'),
        ('musical','Musical'),
        ('spatial','Espacial'),
        ('kinaesthetic','Cinestésica'),
        ('naturalist','Naturalista'),
    ])


class TestQuestion(models.Model):
    _name = 'ml_learning.test_question'
    _description = 'ml_learning.test_question'
    
    exercise_id = fields.Many2one('ml_learning.exercise', string="Pregunta")

    user_id = fields.Many2one('res.users', string="Usuario")

    answered_ok = fields.Boolean("Respondió correcto")

class Level(models.Model):
    _name = 'ml_learning.level'
    _description = 'ml_learning.level'
    
    name = fields.Char("Nivel")

    min_score = fields.Char("Puntaje Minimo")

    max_score = fields.Char("Puntaje Maximo")

    image = fields.Binary("Imagen")


class Progress(models.TransientModel):
    _name = 'ml_learning.progress'
    _description = 'ml_learning.progress'    

    score = fields.Integer("Puntaje Actual")

    level_id = fields.Many2one('ml_learning.level',"Nivel")
    
    level_image = fields.Binary(related="level_id.image")

    @api.model
    def default_get(self, fields):
        res = super(Progress, self).default_get(fields)
        questions = self.env['ml_learning.test_question'].search([('user_id','=',self.env.user.id)])
        score = 0
        for question in questions:
            if question.answered_ok:
                score += 1
        level = self.env['ml_learning.level'].search([('min_score','<=',score),('max_score','>=',score)],limit=1)   
        res['score'] = score
        res['level_id'] = level.id

        return res


class Test(models.TransientModel):
    _name = 'ml_learning.test'
    _description = 'ml_learning.test'

    question = fields.Char("Pregunta")

    answer_1 = fields.Char("Respuesta 1")

    answer_2 = fields.Char("Respuesta 2")

    answer_3 = fields.Char("Respuesta 3")

    answer_4 = fields.Char("Respuesta 4")

    correct_answer = fields.Char()

    answered_ok = fields.Boolean("Respondió correcto")

    selected_answer = fields.Selection([
        ('1','1'),
        ('2','2'),
        ('3','3'),
        ('4','4')
    ], string="Seleccione su respuesta")

    start = fields.Boolean(default=True)

    exercise_ids = fields.Many2many('ml_learning.exercise', string="Preguntas")

    current_pos = fields.Integer(default=0)

    question_ids = fields.Char()

    show_correct_answer_message = fields.Boolean(default=False)

    show_wrong_answer_message = fields.Boolean(default=False)

    def get_question_ids(self):
        #Metodo que llama al modelo y obtiene la recomendacion
        loaded = tf.saved_model.load('/opt/devodoo16/titulacion/saved_model')
        scores, questions = loaded([str(self.env.user.id)])
        return questions
    
    def set_questions(self):
        current_exercise_id = self.env['ml_learning.exercise'].browse(self.exercise_ids.ids[self.current_pos])
        self.question = current_exercise_id.question
        self.answer_1 = current_exercise_id.answer_1
        self.answer_2 = current_exercise_id.answer_2
        self.answer_3 = current_exercise_id.answer_3
        self.answer_4 = current_exercise_id.answer_4
        self.correct_answer = current_exercise_id.correct_answer
        self.current_pos = self.current_pos + 1

    def start_button(self):
        self.start = False
        
        commands = []
        self.get_question_ids()
        for question in [2,3,4,5,6]: #self.get_question_ids():
            commands.append(Command.link(question))

        self.write({'exercise_ids': commands})

        self.set_questions()

        return {
            'name': "Practicar",
            'view_mode': 'form',
            'res_model': 'ml_learning.test',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new',
        }
    
    def check_answer(self):
        correct_answer = "1"
        if self.answer_1 == self.correct_answer:
            correct_answer = "1"
        elif self.answer_2 == self.correct_answer:
            correct_answer = "2"
        elif self.answer_3 == self.correct_answer:
            correct_answer = "3"
        elif self.answer_4 == self.correct_answer:
            correct_answer = "4"
        
        if self.selected_answer == correct_answer:
            self.answered_ok = True
            self.show_correct_answer_message = True
        else:
            self.answered_ok = False
            self.show_wrong_answer_message = True

        self.env['ml_learning.test_question'].create({
            'exercise_id': self.exercise_ids.ids[self.current_pos],
            'user_id': self.env.user.id,
            'answered_ok': self.answered_ok,
        })

        return {
            'name': "Practicar",
            'view_mode': 'form',
            'res_model': 'ml_learning.test',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new',
        }
    
    def next_question(self):
        self.answered_ok = False
        self.show_correct_answer_message = False
        self.show_wrong_answer_message = False
        self.current_pos = self.current_pos + 1
        self.selected_answer = False
        self.set_questions()
        
        return {
            'name': "Practicar",
            'view_mode': 'form',
            'res_model': 'ml_learning.test',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new',
        }