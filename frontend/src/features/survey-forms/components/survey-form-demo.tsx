import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import * as z from 'zod'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import {
    Form,
    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Checkbox } from '@/components/ui/checkbox'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Switch } from '@/components/ui/switch'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

const surveyFormSchema = z.object({
    fullName: z.string().min(2, {
        message: 'Name must be at least 2 characters.',
    }),
    email: z.string().email({
        message: 'Please enter a valid email address.',
    }),
    role: z.string().min(1, {
        message: 'Please select a role.',
    }),
    satisfaction: z.enum(
        ['very-satisfied', 'satisfied', 'neutral', 'dissatisfied', 'very-dissatisfied'] as const,
        {
            message: 'You need to select a satisfaction level.',
        }
    ),
    featuresUsed: z.array(z.string()).refine((value) => value.some((item) => item), {
        message: 'You have to select at least one feature.',
    }),
    feedback: z.string().max(500, {
        message: 'Feedback must not be longer than 500 characters.',
    }).optional(),
    newsletter: z.boolean().default(false).optional(),
})

type SurveyFormValues = z.infer<typeof surveyFormSchema>

const defaultValues: Partial<SurveyFormValues> = {
    featuresUsed: [],
    newsletter: true,
}

const features = [
    { id: 'dashboard', label: 'Dashboard & Reports' },
    { id: 'api', label: 'API Integrations' },
    { id: 'users', label: 'User Management' },
    { id: 'settings', label: 'System Configuration' },
] as const

export function SurveyFormDemo() {
    const form = useForm<SurveyFormValues>({
        resolver: zodResolver(surveyFormSchema),
        defaultValues,
        mode: 'onChange',
    })

    function onSubmit(data: SurveyFormValues) {
        toast.success('Survey Submitted Successfully', {
            description: (
                <pre className="mt-2 w-[340px] rounded-md bg-slate-950 p-4">
                    <code className="text-white">{JSON.stringify(data, null, 2)}</code>
                </pre>
            ),
        })
    }

    return (
        <Card className='shadow-sm border-muted'>
            <CardHeader>
                <CardTitle>Platform Feedback Survey</CardTitle>
                <CardDescription>
                    Help us improve your experience. All fields marked with an asterisk (*) are required.
                </CardDescription>
            </CardHeader>
            <CardContent>
                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <FormField
                                control={form.control}
                                name="fullName"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Full Name *</FormLabel>
                                        <FormControl>
                                            <Input placeholder="John Doe" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />

                            <FormField
                                control={form.control}
                                name="email"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Email Address *</FormLabel>
                                        <FormControl>
                                            <Input type="email" placeholder="john.doe@example.com" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>

                        <FormField
                            control={form.control}
                            name="role"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Primary Role *</FormLabel>
                                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                                        <FormControl>
                                            <SelectTrigger>
                                                <SelectValue placeholder="Select your current role" />
                                            </SelectTrigger>
                                        </FormControl>
                                        <SelectContent>
                                            <SelectItem value="developer">Developer / Engineer</SelectItem>
                                            <SelectItem value="manager">Product Manager</SelectItem>
                                            <SelectItem value="designer">Designer</SelectItem>
                                            <SelectItem value="admin">System Administrator</SelectItem>
                                            <SelectItem value="other">Other</SelectItem>
                                        </SelectContent>
                                    </Select>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="satisfaction"
                            render={({ field }) => (
                                <FormItem className="space-y-3">
                                    <FormLabel>How satisfied are you with our platform? *</FormLabel>
                                    <FormControl>
                                        <RadioGroup
                                            onValueChange={field.onChange}
                                            defaultValue={field.value}
                                            className="flex flex-col space-y-1 sm:flex-row sm:space-x-4 sm:space-y-0"
                                        >
                                            <FormItem className="flex items-center space-x-2 space-y-0">
                                                <FormControl>
                                                    <RadioGroupItem value="very-satisfied" />
                                                </FormControl>
                                                <FormLabel className="font-normal cursor-pointer">
                                                    Very Satisfied
                                                </FormLabel>
                                            </FormItem>
                                            <FormItem className="flex items-center space-x-2 space-y-0">
                                                <FormControl>
                                                    <RadioGroupItem value="satisfied" />
                                                </FormControl>
                                                <FormLabel className="font-normal cursor-pointer">
                                                    Satisfied
                                                </FormLabel>
                                            </FormItem>
                                            <FormItem className="flex items-center space-x-2 space-y-0">
                                                <FormControl>
                                                    <RadioGroupItem value="neutral" />
                                                </FormControl>
                                                <FormLabel className="font-normal cursor-pointer">
                                                    Neutral
                                                </FormLabel>
                                            </FormItem>
                                            <FormItem className="flex items-center space-x-2 space-y-0">
                                                <FormControl>
                                                    <RadioGroupItem value="dissatisfied" />
                                                </FormControl>
                                                <FormLabel className="font-normal cursor-pointer">
                                                    Dissatisfied
                                                </FormLabel>
                                            </FormItem>
                                        </RadioGroup>
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="featuresUsed"
                            render={() => (
                                <FormItem>
                                    <div className="mb-4">
                                        <FormLabel className="text-base">Features Used *</FormLabel>
                                        <FormDescription>
                                            Select the features you interact with the most.
                                        </FormDescription>
                                    </div>
                                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                        {features.map((item) => (
                                            <FormField
                                                key={item.id}
                                                control={form.control}
                                                name="featuresUsed"
                                                render={({ field }) => {
                                                    return (
                                                        <FormItem
                                                            key={item.id}
                                                            className="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4 shadow-sm"
                                                        >
                                                            <FormControl>
                                                                <Checkbox
                                                                    checked={field.value?.includes(item.id)}
                                                                    onCheckedChange={(checked) => {
                                                                        return checked
                                                                            ? field.onChange([...field.value, item.id])
                                                                            : field.onChange(
                                                                                field.value?.filter(
                                                                                    (value) => value !== item.id
                                                                                )
                                                                            )
                                                                    }}
                                                                />
                                                            </FormControl>
                                                            <FormLabel className="font-normal cursor-pointer flex-1">
                                                                {item.label}
                                                            </FormLabel>
                                                        </FormItem>
                                                    )
                                                }}
                                            />
                                        ))}
                                    </div>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="feedback"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Additional Feedback</FormLabel>
                                    <FormControl>
                                        <Textarea
                                            placeholder="Tell us what you like or what could be improved..."
                                            className="resize-none"
                                            rows={5}
                                            {...field}
                                        />
                                    </FormControl>
                                    <FormDescription>
                                        Maximum 500 characters.
                                    </FormDescription>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="newsletter"
                            render={({ field }) => (
                                <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                                    <div className="space-y-0.5">
                                        <FormLabel className="text-base">
                                            Communication Preferences
                                        </FormLabel>
                                        <FormDescription>
                                            Receive emails about platform updates and release notes.
                                        </FormDescription>
                                    </div>
                                    <FormControl>
                                        <Switch
                                            checked={field.value}
                                            onCheckedChange={field.onChange}
                                        />
                                    </FormControl>
                                </FormItem>
                            )}
                        />

                        <div className="flex justify-end pt-4">
                            <Button type="submit" size="lg" className="w-full sm:w-auto">
                                Submit Survey
                            </Button>
                        </div>
                    </form>
                </Form>
            </CardContent>
        </Card>
    )
}
