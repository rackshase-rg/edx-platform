"""
Progress Tab Serializers
"""
from rest_framework import serializers
from lms.djangoapps.course_home_api.outline.v1.serializers import CourseBlockSerializer
from rest_framework.reverse import reverse


class CoursewareSummarySerializer(serializers.Serializer):
    """
    Serializer for the courseware summary blocks
    """
    blocks = serializers.SerializerMethodField()

    def get_blocks(self, blocks):
        return [
            {
                'display_name': chapter['display_name'],
                'chapter_url': reverse(  # currently points to the LMS url not the MFE
                    'jump_to',
                    kwargs={'course_id': str(self.context['course_key']), 'location': str(chapter['url_name'])},
                    request=self.context['request'],
                ),
                'sections': [
                    {
                        'display_name': section.display_name,
                        'section_url': self.context['request'].build_absolute_uri(reverse(
                            'courseware_section',
                            kwargs={'course_id': str(self.context['course_key']), 'chapter': chapter['url_name'],
                                    'section': section.url_name})),
                        'percent_graded': section.percent_graded,
                        'graded_total': {
                            'first_attempted': section.graded_total.first_attempted,
                            'possible': section.graded_total.possible,
                            'graded': section.graded_total.graded,
                            'earned': section.graded_total.earned,
                        },
                        'format': section.format,
                        'due': section.due,
                        'override': section.override,  # TODO: update to correct serializer
                        'show_correctness': section.show_correctness,
                        'graded': section.graded,
                        'problem_scores': [
                            {
                                'earned': score.earned,
                                'possible': score.possible,
                            }
                            for score in section.problem_scores.values()
                        ],
                        'show_grades': section.show_grades(self.context['staff_access'])
                    }
                    for section in chapter['sections']
                ],
            }
            for chapter in blocks
        ]


class ProgressTabSerializer(serializers.Serializer):
    """
    Serializer for progress tab
    """
    course_blocks = CourseBlockSerializer()
    enrollment_mode = serializers.CharField()
    courseware_summary = CoursewareSummarySerializer()
    is_self_paced = serializers.BooleanField()
    user_timezone = serializers.CharField()
