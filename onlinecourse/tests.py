from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Choice, Course, Enrollment, Question, Submission


class ExamFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('learner')
        self.course = Course.objects.create(name='Learning Django', description='Demo')
        Enrollment.objects.create(user=self.user, course=self.course)
        self.question = Question.objects.create(course=self.course, question_text='Select both correct answers', grade=100)
        self.correct_a = Choice.objects.create(question=self.question, choice_text='A', is_correct=True)
        self.correct_b = Choice.objects.create(question=self.question, choice_text='B', is_correct=True)
        self.wrong = Choice.objects.create(question=self.question, choice_text='C')
        self.client.force_login(self.user)

    def test_correct_multiselect_submission_passes(self):
        response = self.client.post(reverse('onlinecourse:submit', args=[self.course.id]), {
            f'choice_{self.correct_a.id}': self.correct_a.id,
            f'choice_{self.correct_b.id}': self.correct_b.id,
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Congratulations')
        self.assertContains(response, '100/100')
        self.assertEqual(Submission.objects.count(), 1)

    def test_extra_wrong_choice_does_not_earn_score(self):
        response = self.client.post(reverse('onlinecourse:submit', args=[self.course.id]), {
            f'choice_{self.correct_a.id}': self.correct_a.id,
            f'choice_{self.correct_b.id}': self.correct_b.id,
            f'choice_{self.wrong.id}': self.wrong.id,
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '0/100')
        self.assertContains(response, 'Wrong answer: C')

    def test_choice_from_another_course_is_rejected(self):
        another = Course.objects.create(name='Another course', description='Demo')
        question = Question.objects.create(course=another, question_text='Other')
        other_choice = Choice.objects.create(question=question, choice_text='Other answer')
        response = self.client.post(reverse('onlinecourse:submit', args=[self.course.id]), {
            f'choice_{other_choice.id}': other_choice.id,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Submission.objects.count(), 0)

    def test_other_learner_cannot_view_result(self):
        submission = Submission.objects.create(enrollment=Enrollment.objects.get(user=self.user))
        other_user = User.objects.create_user('another')
        self.client.force_login(other_user)
        response = self.client.get(reverse('onlinecourse:show_exam_result',
                                           args=[self.course.id, submission.id]))
        self.assertEqual(response.status_code, 404)

    def test_course_detail_and_named_result_route(self):
        response = self.client.get(reverse('onlinecourse:course_details', args=[self.course.id]))
        self.assertContains(response, 'Select both correct answers')
        self.assertContains(response, 'A')
        submission = Submission.objects.create(enrollment=Enrollment.objects.get(user=self.user))
        self.assertIn('learner', str(submission))
        result = self.client.get(reverse('onlinecourse:show_exam_result',
                                         args=[self.course.id, submission.id]))
        self.assertEqual(result.status_code, 200)
